# Restaurant Management System

A REST API-based Restaurant Management System developed using **Python, Django, and Django REST Framework**.

This project helps restaurants manage their menu, tables, reservations, inventory, and customer orders through RESTful APIs.

## Features

- **Category Management:** Create, view, update, and manage food categories.
- **Menu Management:** Manage menu items, descriptions, prices, and availability.
- **Table Management:** Manage restaurant tables, seating capacity, and table status.
- **Reservation Management:** Create and manage reservations with time-conflict and seating-capacity validation.
- **Inventory Management:** Track ingredient quantities and identify low-stock items.
- **Order Management:** Create and manage customer orders with automatic total calculation.
- **Automatic Stock Management:** Deduct ingredient quantities when orders are placed and restore stock when orders are cancelled.
- **Input Validation:** Validate prices, quantities, reservations, and available stock.

## Technologies Used

- Python
- Django
- Django REST Framework
- SQLite
- REST API
- Git and GitHub

## Project Structure

```text
CodeAlpha_RestaurantManagement/
│
├── config/
│   └── Django project configuration
│
├── restaurant/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
└── db.sqlite3
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CodeAlpha_RestaurantManagement
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an administrator account

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The application will run at:

`http://127.0.0.1:8000/`

## API Endpoints

| Module | Endpoint |
|---|---|
| Categories | `/api/categories/` |
| Category Details | `/api/categories/<id>/` |
| Menu Items | `/api/menu/` |
| Menu Item Details | `/api/menu/<id>/` |
| Tables | `/api/tables/` |
| Table Details | `/api/tables/<id>/` |
| Reservations | `/api/reservations/` |
| Reservation Details | `/api/reservations/<id>/` |
| Inventory | `/api/inventory/` |
| Inventory Details | `/api/inventory/<id>/` |
| Orders | `/api/orders/` |
| Order Details | `/api/orders/<id>/` |

## Example: Create an Order

**POST** `/api/orders/`

```json
{
  "customer_name": "Test Customer",
  "table": 1,
  "order_items": [
    {
      "menu_item": 1,
      "quantity": 2
    }
  ]
}
```

The system automatically calculates the order total using menu prices and deducts the required ingredients from inventory.

When an order is cancelled, the deducted ingredient quantities are restored.

## Filtering

The API supports filtering:

- Menu items by category: `GET /api/menu/?category=1`
- Tables by status: `GET /api/tables/?status=available`
- Reservations by date: `GET /api/reservations/?date=2026-11-05`
- Reservations by table: `GET /api/reservations/?table=1`
- Reservations by status: `GET /api/reservations/?status=confirmed`
- Low-stock inventory: `GET /api/inventory/?low_stock=true`
- Orders by status: `GET /api/orders/?status=pending`
- Orders by table: `GET /api/orders/?table=1`

## Testing

The project includes automated tests using Django TestCase and Django REST Framework APIClient.

Run the test suite:

```bash
python manage.py test restaurant
```

**Test Result:** 30 tests passed successfully.

## Admin Panel

Access the Django administration panel:

`http://127.0.0.1:8000/admin/`

Log in using your superuser credentials.

## Project Information

**Internship:** CodeAlpha

**Project:** Restaurant Management System

**Development:** Python Backend Development

---

Developed as part of the CodeAlpha Backend Development Internship.