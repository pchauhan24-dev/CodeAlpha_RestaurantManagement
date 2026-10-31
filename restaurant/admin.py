
from django.contrib import admin
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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name",)


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ("id", "table_number", "capacity", "status")
    list_filter = ("status",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "table",
        "reservation_date",
        "reservation_time",
        "number_of_guests",
        "status",
    )
    list_filter = ("status", "reservation_date")
    search_fields = ("customer_name", "customer_email")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "quantity",
        "unit",
        "low_stock_threshold",
    )
    search_fields = ("name",)


@admin.register(MenuItemIngredient)
class MenuItemIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "menu_item",
        "inventory_item",
        "quantity_required",
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "table",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("customer_name",)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "menu_item",
        "quantity",
        "unit_price",
        "subtotal",
    )
