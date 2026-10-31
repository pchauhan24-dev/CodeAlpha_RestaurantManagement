
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from .models import (
    Category,
    MenuItem,
    RestaurantTable,
    Reservation,
    InventoryItem,
    MenuItemIngredient,
    Order,
    OrderItem,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )
        return value


class RestaurantTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantTable
        fields = "__all__"
        read_only_fields = ("id",)

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Table capacity must be at least 1."
            )
        return value


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        start_time = attrs.get(
            "reservation_time",
            getattr(self.instance, "reservation_time", None)
        )
        end_time = attrs.get(
            "reservation_end_time",
            getattr(self.instance, "reservation_end_time", None)
        )
        table = attrs.get(
            "table",
            getattr(self.instance, "table", None)
        )
        guests = attrs.get(
            "number_of_guests",
            getattr(self.instance, "number_of_guests", None)
        )
        reservation_date = attrs.get(
            "reservation_date",
            getattr(self.instance, "reservation_date", None)
        )
        reservation_status = attrs.get(
            "status",
            getattr(self.instance, "status", "confirmed")
        )

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                "Reservation end time must be later than start time."
            )

        if table and guests and guests > table.capacity:
            raise serializers.ValidationError(
                "Number of guests cannot exceed table capacity."
            )

        if (
            table
            and reservation_date
            and start_time
            and end_time
            and reservation_status == "confirmed"
        ):
            overlapping = Reservation.objects.filter(
                table=table,
                reservation_date=reservation_date,
                status="confirmed",
                reservation_time__lt=end_time,
                reservation_end_time__gt=start_time,
            )

            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError(
                    "This table already has a reservation during this time."
                )

        return attrs


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = "__all__"
        read_only_fields = ("id", "updated_at")

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )
        return value

    def validate_low_stock_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Low stock threshold cannot be negative."
            )
        return value


# ------------------------------------------
# ORDER ITEM INPUT
# ------------------------------------------

class OrderItemInputSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)


# ------------------------------------------
# ORDER ITEM OUTPUT
# ------------------------------------------

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(
        source="menu_item.name",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "menu_item",
            "menu_item_name",
            "quantity",
            "unit_price",
            "subtotal",
        )
        read_only_fields = fields


# ------------------------------------------
# ORDER SERIALIZER
# ------------------------------------------

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_items = OrderItemInputSerializer(
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "table",
            "customer_name",
            "status",
            "total_amount",
            "created_at",
            "items",
            "order_items",
        )
        read_only_fields = ("id", "total_amount", "created_at")

    def validate(self, attrs):
        if not self.instance and not attrs.get("order_items"):
            raise serializers.ValidationError({
                "order_items": "At least one order item is required."
            })

        if self.instance and "order_items" in attrs:
            raise serializers.ValidationError({
                "order_items": "Order items cannot be changed after creation."
            })

        if (
            self.instance
            and self.instance.status == Order.Status.CANCELLED
            and attrs.get("status", self.instance.status) != Order.Status.CANCELLED
        ):
            raise serializers.ValidationError(
                "A cancelled order cannot be reopened."
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")
        required_stock = {}

        # Calculate all ingredient quantities required.
        for item_data in order_items_data:
            menu_item = item_data["menu_item"]
            quantity = item_data["quantity"]

            if not menu_item.is_available:
                raise serializers.ValidationError({
                    "order_items": f"{menu_item.name} is currently unavailable."
                })

            ingredients = MenuItemIngredient.objects.filter(
                menu_item=menu_item
            ).select_related("inventory_item")

            for ingredient in ingredients:
                inventory_id = ingredient.inventory_item.pk
                amount = ingredient.quantity_required * quantity

                if inventory_id not in required_stock:
                    required_stock[inventory_id] = {
                        "amount": Decimal("0"),
                        "name": ingredient.inventory_item.name,
                    }

                required_stock[inventory_id]["amount"] += amount

        # Lock inventory rows and check stock before deducting.
        locked_inventory = {}

        for inventory_id, details in required_stock.items():
            inventory = InventoryItem.objects.select_for_update().get(
                pk=inventory_id
            )

            if inventory.quantity < details["amount"]:
                raise serializers.ValidationError({
                    "inventory": (
                        f"Insufficient stock for {inventory.name}. "
                        f"Available: {inventory.quantity}, "
                        f"Required: {details['amount']}."
                    )
                })

            locked_inventory[inventory_id] = inventory

        # Deduct ingredient stock.
        for inventory_id, details in required_stock.items():
            inventory = locked_inventory[inventory_id]
            inventory.quantity -= details["amount"]
            inventory.save(update_fields=["quantity", "updated_at"])

        # Create order and order items using current menu prices.
        order = Order.objects.create(**validated_data)
        total = Decimal("0")

        for item_data in order_items_data:
            menu_item = item_data["menu_item"]
            quantity = item_data["quantity"]
            unit_price = menu_item.price
            subtotal = unit_price * quantity

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )

            total += subtotal

        order.total_amount = total
        order.save(update_fields=["total_amount"])

        return order

    
    @transaction.atomic
    def update(self, instance, validated_data):
        # Always get the latest order status from the database.
        instance.refresh_from_db()

        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        # Restore ingredients only during the first transition
        # from a non-cancelled status to cancelled.
        if (
            old_status != Order.Status.CANCELLED
            and new_status == Order.Status.CANCELLED
        ):
            stock_to_restore = {}

            order_items = instance.items.select_related(
                "menu_item"
            ).all()

            for order_item in order_items:
                ingredients = MenuItemIngredient.objects.filter(
                    menu_item_id=order_item.menu_item_id
                )

                for ingredient in ingredients:
                    inventory_id = ingredient.inventory_item.pk

                    amount = (
                        ingredient.quantity_required
                        * order_item.quantity
                    )

                    stock_to_restore[inventory_id] = (
                        stock_to_restore.get(
                            inventory_id,
                            Decimal("0")
                        ) + amount
                    )

            # Restore each inventory item.
            for inventory_id, amount in stock_to_restore.items():
                inventory = InventoryItem.objects.select_for_update().get(
                    pk=inventory_id
                )

                inventory.quantity += amount

                inventory.save(
                    update_fields=["quantity", "updated_at"]
                )

        # Save the order's new status and other permitted fields.
        return super().update(instance, validated_data)
