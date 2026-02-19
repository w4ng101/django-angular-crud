# Django + Angular CRUD Application

A full-stack CRUD application built with Django REST Framework (backend) and Angular (frontend).

## Project Overview

This application allows users to create, read, update, and delete **Items**. Each item has a name, description, and a creation timestamp.

- **Backend**: Django 4.2+ with Django REST Framework, served at `http://localhost:8000`
- **Frontend**: Angular 21+ (standalone components), served at `http://localhost:4200`

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+
- Angular CLI (`npm install -g @angular/cli`)

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`.

### Create a superuser (optional)

```bash
python manage.py createsuperuser
```

Then access the Django admin at `http://localhost:8000/admin/`.

## Frontend Setup

```bash
cd frontend
npm install
ng serve
```

The app will be available at `http://localhost:4200`.

## API Documentation

Base URL: `http://localhost:8000/api/`

| Method | Endpoint           | Description         |
|--------|--------------------|---------------------|
| GET    | `/api/items/`      | List all items      |
| POST   | `/api/items/`      | Create a new item   |
| GET    | `/api/items/{id}/` | Retrieve an item    |
| PUT    | `/api/items/{id}/` | Update an item      |
| PATCH  | `/api/items/{id}/` | Partially update    |
| DELETE | `/api/items/{id}/` | Delete an item      |

### Item Schema

```json
{
  "id": 1,
  "name": "Sample Item",
  "description": "A description of the item",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Example Requests

**List items:**
```bash
curl http://localhost:8000/api/items/
```

**Create item:**
```bash
curl -X POST http://localhost:8000/api/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Item", "description": "A description"}'
```

**Update item:**
```bash
curl -X PUT http://localhost:8000/api/items/1/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item", "description": "Updated description"}'
```

**Delete item:**
```bash
curl -X DELETE http://localhost:8000/api/items/1/
```

## Project Structure

```
django-angular-crud/
├── backend/                  # Django backend
│   ├── backend/              # Django project settings
│   │   ├── settings.py
│   │   └── urls.py
│   ├── items/                # Items app
│   │   ├── models.py         # Item model
│   │   ├── serializers.py    # DRF serializer
│   │   ├── views.py          # ViewSet
│   │   └── urls.py           # Router URLs
│   ├── requirements.txt
│   └── manage.py
└── frontend/                 # Angular frontend
    └── src/
        └── app/
            ├── item.ts               # Item interface
            ├── item.service.ts       # HTTP service
            ├── item-list/            # List component
            └── item-form/            # Create/Edit component
```
