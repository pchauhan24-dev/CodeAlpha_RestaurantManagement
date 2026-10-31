
from django.db import models
from decimal import Decimal


# ------------------------------------------
# MENU CATEGORY
# ------------------------------------------

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# ------------------------------------------
# MENU ITEMS
# ------------------------------------------

class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="menu_items"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ------------------------------------------
# RESTAURANT TABLES
# ------------------------------------------

class RestaurantTable(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        RESERVED = "reserved", "Reserved"

    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )

    def __str__(self):
        return f"Table {self.table_number}"


# ------------------------------------------
# TABLE RESERVATIONS
# ------------------------------------------

class Reservation(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.PROTECT,
        related_name="reservations"
    )
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    reservation_end_time = models.TimeField(null=True, blank=True)
    number_of_guests = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - Table {self.table.table_number}"


# ------------------------------------------
# INVENTORY ITEMS
# ------------------------------------------

class InventoryItem(models.Model):
    name = models.CharField(max_length=150, unique=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=30)
    low_stock_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("5")
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ------------------------------------------
# MENU ITEM INGREDIENTS
# ------------------------------------------

class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="ingredients"
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name="used_in"
    )
    quantity_required = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["menu_item", "inventory_item"],
                name="unique_menu_item_ingredient"
            )
        ]

    def __str__(self):
        return f"{self.inventory_item.name} for {self.menu_item.name}"


# ------------------------------------------
# CUSTOMER ORDERS
# ------------------------------------------

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    table = models.ForeignKey(
        RestaurantTable,
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True
    )
    customer_name = models.CharField(max_length=150)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer_name}"


# ------------------------------------------
# ORDER ITEMS
# ------------------------------------------

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"
