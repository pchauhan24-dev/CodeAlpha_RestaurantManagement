
from rest_framework import generics
from django.db import models
from .models import Order
from .serializers import OrderSerializer
from .models import (
    Category,
    MenuItem,
    RestaurantTable,
    Reservation,
    InventoryItem,
)

from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    RestaurantTableSerializer,
    ReservationSerializer,
    InventoryItemSerializer,
)


# ------------------------------------------
# CATEGORY LIST AND CREATE
# ------------------------------------------

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer


# ------------------------------------------
# CATEGORY DETAILS, UPDATE AND DELETE
# ------------------------------------------

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ------------------------------------------
# MENU ITEM LIST AND CREATE
# ------------------------------------------

class MenuItemListCreateView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        queryset = MenuItem.objects.select_related("category").all()

        category_id = self.request.GET.get("category")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by("name")


# ------------------------------------------
# MENU ITEM DETAILS, UPDATE AND DELETE
# ------------------------------------------

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer


# ------------------------------------------
# TABLE LIST AND CREATE
# ------------------------------------------

class RestaurantTableListCreateView(generics.ListCreateAPIView):
    serializer_class = RestaurantTableSerializer

    def get_queryset(self):
        queryset = RestaurantTable.objects.all().order_by(
            "table_number"
        )

        table_status = self.request.GET.get("status")

        if table_status:
            queryset = queryset.filter(status=table_status)

        return queryset


# ------------------------------------------
# TABLE DETAILS, UPDATE AND DELETE
# ------------------------------------------

class RestaurantTableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableSerializer



# RESERVATION LIST AND CREATE
class ReservationListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = Reservation.objects.select_related("table").all()

        reservation_date = self.request.GET.get("date")
        table_id = self.request.GET.get("table")
        reservation_status = self.request.GET.get("status")

        if reservation_date:
            queryset = queryset.filter(
                reservation_date=reservation_date
            )

        if table_id:
            queryset = queryset.filter(table_id=table_id)

        if reservation_status:
            queryset = queryset.filter(status=reservation_status)

        return queryset.order_by("reservation_date", "reservation_time")


# RESERVATION DETAILS, UPDATE AND DELETE
class ReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.select_related("table").all()
    serializer_class = ReservationSerializer



# INVENTORY LIST AND CREATE
class InventoryItemListCreateView(generics.ListCreateAPIView):
    serializer_class = InventoryItemSerializer

    def get_queryset(self):
        queryset = InventoryItem.objects.all().order_by("name")

        low_stock = self.request.GET.get("low_stock")

        if low_stock == "true":
            queryset = queryset.filter(
                quantity__lte=models.F("low_stock_threshold")
            )

        return queryset


# INVENTORY DETAILS, UPDATE AND DELETE
class InventoryItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer


# ------------------------------------------
# ORDER API
# ------------------------------------------

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.prefetch_related(
            "items__menu_item"
        ).order_by("-created_at")

        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        table_filter = self.request.GET.get("table")
        if table_filter:
            queryset = queryset.filter(table_id=table_filter)

        return queryset


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.prefetch_related("items__menu_item")
    serializer_class = OrderSerializer