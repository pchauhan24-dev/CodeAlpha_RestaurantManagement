
from django.urls import path
from .views import OrderListCreateView, OrderDetailView
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    MenuItemListCreateView,
    MenuItemDetailView,
    RestaurantTableListCreateView,
    RestaurantTableDetailView,
    ReservationListCreateView,
    ReservationDetailView,
    InventoryItemListCreateView,
    InventoryItemDetailView,
)

urlpatterns = [
    # Category APIs
    path(
        "categories/",
        CategoryListCreateView.as_view(),
        name="category-list-create"
    ),
    path(
        "categories/<int:pk>/",
        CategoryDetailView.as_view(),
        name="category-detail"
    ),

    # Menu APIs
    path(
        "menu/",
        MenuItemListCreateView.as_view(),
        name="menu-list-create"
    ),
    path(
        "menu/<int:pk>/",
        MenuItemDetailView.as_view(),
        name="menu-detail"
    ),

    path(
    "tables/",
    RestaurantTableListCreateView.as_view(),
    name="table-list-create"
    ),
    path(
    "tables/<int:pk>/",
    RestaurantTableDetailView.as_view(),
    name="table-detail"
    ),
    path(
    "reservations/",
    ReservationListCreateView.as_view(),
    name="reservation-list-create",
    ),

    path(
    "reservations/<int:pk>/",
    ReservationDetailView.as_view(),
    name="reservation-detail",
    ),

    path(
    "inventory/",
    InventoryItemListCreateView.as_view(),
    name="inventory-list-create",
    ),

    path(
    "inventory/<int:pk>/",
    InventoryItemDetailView.as_view(),
    name="inventory-detail",
    ),

    path(
    "orders/",
    OrderListCreateView.as_view(), 
    name="order-list-create"
    ),

    path(
    "orders/<int:pk>/", 
    OrderDetailView.as_view(), 
    name="order-detail"
    ),
]
