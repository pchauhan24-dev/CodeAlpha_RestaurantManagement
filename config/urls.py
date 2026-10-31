
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def home(request):
    return JsonResponse({
        "message": "Welcome to the Restaurant Management System API!",
        "endpoints": {
            "admin": "/admin/",
            "api": "/api/",
            "menu": "/api/menu/",
            "tables": "/api/tables/",
            "reservations": "/api/reservations/",
            "inventory": "/api/inventory/",
            "orders": "/api/orders/",
        }
    })


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("restaurant.urls")),
]
