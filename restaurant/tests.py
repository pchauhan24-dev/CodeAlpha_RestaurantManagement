from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    Category,
    MenuItem,
    RestaurantTable,
    Reservation,
    InventoryItem,
    MenuItemIngredient,
    Order,
)


# ==========================================
# MENU API TESTS
# ==========================================

class MenuAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(
            name="Pizza",
            description="Fresh pizzas"
        )

        self.menu_item = MenuItem.objects.create(
            category=self.category,
            name="Margherita Pizza",
            description="Cheese and tomato pizza",
            price="299.00",
            is_available=True
        )

    def test_category_list(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_creation(self):
        data = {
            "name": "Beverages",
            "description": "Cold and hot drinks"
        }

        response = self.client.post(
            "/api/categories/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_menu_item_list(self):
        response = self.client.get("/api/menu/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_menu_item_creation(self):
        category = Category.objects.create(name="Desserts")

        data = {
            "category": category.pk,
            "name": "Chocolate Cake",
            "description": "Chocolate dessert",
            "price": "150.00",
            "is_available": True
        }

        response = self.client.post(
            "/api/menu/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_menu_item_filter_by_category(self):
        response = self.client.get(
            f"/api/menu/?category={self.category.pk}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_menu_item_rejects_zero_price(self):
        data = {
            "category": self.category.pk,
            "name": "Invalid Pizza",
            "description": "Invalid price test",
            "price": "0.00",
            "is_available": True
        }

        response = self.client.post(
            "/api/menu/", data, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )


# ==========================================
# RESTAURANT TABLE API TESTS
# ==========================================

class RestaurantTableAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.table = RestaurantTable.objects.create(
            table_number=1,
            capacity=4,
            status="available"
        )

    def test_table_list(self):
        response = self.client.get("/api/tables/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_table_creation(self):
        data = {
            "table_number": 2,
            "capacity": 2,
            "status": "available"
        }

        response = self.client.post(
            "/api/tables/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_table_details(self):
        response = self.client.get(
            f"/api/tables/{self.table.pk}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_table_update(self):
        data = {
            "capacity": 6,
            "status": "occupied"
        }

        response = self.client.patch(
            f"/api/tables/{self.table.pk}/",
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_table_filter_by_status(self):
        response = self.client.get("/api/tables/?status=available")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_table_rejects_zero_capacity(self):
        data = {
            "table_number": 2,
            "capacity": 0,
            "status": "available"
        }

        response = self.client.post(
            "/api/tables/", data, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )


# ==========================================
# RESERVATION API TESTS
# ==========================================

class ReservationAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.table = RestaurantTable.objects.create(
            table_number=1,
            capacity=4,
            status="available"
        )

        self.reservation_data = {
            "table": self.table.pk,
            "customer_name": "Rahul Sharma",
            "customer_email": "rahul@example.com",
            "reservation_date": "2026-11-05",
            "reservation_time": "18:00:00",
            "reservation_end_time": "20:00:00",
            "number_of_guests": 3,
            "status": "confirmed"
        }

    def test_reservation_creation(self):
        response = self.client.post(
            "/api/reservations/",
            self.reservation_data,
            format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )

    def test_reservation_list(self):
        self.client.post(
            "/api/reservations/",
            self.reservation_data,
            format="json"
        )

        response = self.client.get("/api/reservations/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_reject_guests_exceeding_capacity(self):
        data = self.reservation_data.copy()
        data["number_of_guests"] = 5

        response = self.client.post(
            "/api/reservations/", data, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_reject_overlapping_reservation(self):
        self.client.post(
            "/api/reservations/",
            self.reservation_data,
            format="json"
        )

        data = self.reservation_data.copy()
        data["customer_name"] = "Amit Verma"
        data["customer_email"] = "amit@example.com"
        data["reservation_time"] = "19:00:00"
        data["reservation_end_time"] = "21:00:00"

        response = self.client.post(
            "/api/reservations/", data, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_allow_non_overlapping_reservation(self):
        self.client.post(
            "/api/reservations/",
            self.reservation_data,
            format="json"
        )

        data = self.reservation_data.copy()
        data["reservation_time"] = "20:00:00"
        data["reservation_end_time"] = "22:00:00"

        response = self.client.post(
            "/api/reservations/", data, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )

    def test_reject_end_time_before_start_time(self):
        data = self.reservation_data.copy()
        data["reservation_time"] = "20:00:00"
        data["reservation_end_time"] = "18:00:00"

        response = self.client.post(
            "/api/reservations/", data, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )


# ==========================================
# INVENTORY API TESTS
# ==========================================

class InventoryAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.inventory_item = InventoryItem.objects.create(
            name="Pizza Flour",
            quantity=Decimal("20.00"),
            unit="kg",
            low_stock_threshold=Decimal("5.00")
        )

    def test_inventory_list(self):
        response = self.client.get("/api/inventory/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inventory_item_creation(self):
        data = {
            "name": "Cheese",
            "quantity": "10.00",
            "unit": "kg",
            "low_stock_threshold": "3.00"
        }

        response = self.client.post(
            "/api/inventory/", data, format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )

    def test_inventory_item_update(self):
        response = self.client.patch(
            f"/api/inventory/{self.inventory_item.pk}/",
            {"quantity": "15.00"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.inventory_item.refresh_from_db()
        self.assertEqual(
            self.inventory_item.quantity, Decimal("15.00")
        )

    def test_low_stock_filter(self):
        self.inventory_item.quantity = Decimal("2.00")
        self.inventory_item.save()

        response = self.client.get("/api/inventory/?low_stock=true")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_reject_negative_inventory_quantity(self):
        response = self.client.patch(
            f"/api/inventory/{self.inventory_item.pk}/",
            {"quantity": "-5.00"},
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_reject_negative_low_stock_threshold(self):
        response = self.client.patch(
            f"/api/inventory/{self.inventory_item.pk}/",
            {"low_stock_threshold": "-2.00"},
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )


# ==========================================
# ORDER API TESTS
# ==========================================

class OrderAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.category = Category.objects.create(
            name="Pizza",
            description="Fresh pizzas"
        )

        self.menu_item = MenuItem.objects.create(
            category=self.category,
            name="Margherita Pizza",
            description="Cheese and tomato pizza",
            price=Decimal("299.00"),
            is_available=True
        )

        self.table = RestaurantTable.objects.create(
            table_number=1,
            capacity=4,
            status="available"
        )

        self.flour = InventoryItem.objects.create(
            name="Pizza Flour",
            quantity=Decimal("20.00"),
            unit="kg",
            low_stock_threshold=Decimal("5.00")
        )

        self.cheese = InventoryItem.objects.create(
            name="Cheese",
            quantity=Decimal("10.00"),
            unit="kg",
            low_stock_threshold=Decimal("3.00")
        )

        self.sauce = InventoryItem.objects.create(
            name="Tomato Sauce",
            quantity=Decimal("10.00"),
            unit="litres",
            low_stock_threshold=Decimal("5.00")
        )

        MenuItemIngredient.objects.create(
            menu_item=self.menu_item,
            inventory_item=self.flour,
            quantity_required=Decimal("0.25")
        )

        MenuItemIngredient.objects.create(
            menu_item=self.menu_item,
            inventory_item=self.cheese,
            quantity_required=Decimal("0.15")
        )

        MenuItemIngredient.objects.create(
            menu_item=self.menu_item,
            inventory_item=self.sauce,
            quantity_required=Decimal("0.10")
        )

        self.order_data = {
            "customer_name": "Test Customer",
            "table": self.table.pk,
            "order_items": [
                {
                    "menu_item": self.menu_item.pk,
                    "quantity": 2
                }
            ]
        }

    def test_order_creation_and_total_calculation(self):
        response = self.client.post(
            "/api/orders/",
            self.order_data,
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )

        order = Order.objects.get(pk=response.json()["id"])

        self.assertEqual(order.total_amount, Decimal("598.00"))
        self.assertEqual(getattr(order, "items").count(), 1)

    def test_order_creation_deducts_inventory(self):
        response = self.client.post(
            "/api/orders/",
            self.order_data,
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )

        self.flour.refresh_from_db()
        self.cheese.refresh_from_db()
        self.sauce.refresh_from_db()

        self.assertEqual(self.flour.quantity, Decimal("19.50"))
        self.assertEqual(self.cheese.quantity, Decimal("9.70"))
        self.assertEqual(self.sauce.quantity, Decimal("9.80"))

    def test_insufficient_stock_rejects_order(self):
        self.flour.quantity = Decimal("0.10")
        self.flour.save()

        response = self.client.post(
            "/api/orders/",
            self.order_data,
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(Order.objects.count(), 0)

        self.flour.refresh_from_db()
        self.assertEqual(self.flour.quantity, Decimal("0.10"))

    def test_cancelling_order_restores_inventory(self):
        response = self.client.post(
            "/api/orders/",
            self.order_data,
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )

        order_id = response.json()["id"]

        cancel_response = self.client.patch(
            f"/api/orders/{order_id}/",
            {"status": "cancelled"},
            format="json"
        )

        self.assertEqual(
            cancel_response.status_code, status.HTTP_200_OK
        )

        self.flour.refresh_from_db()
        self.cheese.refresh_from_db()
        self.sauce.refresh_from_db()

        self.assertEqual(self.flour.quantity, Decimal("20.00"))
        self.assertEqual(self.cheese.quantity, Decimal("10.00"))
        self.assertEqual(self.sauce.quantity, Decimal("10.00"))

    def test_repeated_cancellation_does_not_restore_stock_twice(self):
        response = self.client.post(
            "/api/orders/",
            self.order_data,
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )

        order_id = response.json()["id"]

        self.client.patch(
            f"/api/orders/{order_id}/",
            {"status": "cancelled"},
            format="json"
        )

        self.flour.refresh_from_db()
        self.assertEqual(self.flour.quantity, Decimal("20.00"))

        second_response = self.client.patch(
            f"/api/orders/{order_id}/",
            {"status": "cancelled"},
            format="json"
        )

        self.assertEqual(
            second_response.status_code, status.HTTP_200_OK
        )

        self.flour.refresh_from_db()
        self.assertEqual(self.flour.quantity, Decimal("20.00"))

    def test_unavailable_menu_item_rejects_order(self):
        self.menu_item.is_available = False
        self.menu_item.save()

        response = self.client.post(
            "/api/orders/",
            self.order_data,
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(Order.objects.count(), 0)