# Django Angular CRUD Application

A full-stack web application built with Django 5.2.11, Angular 21.1.0, and PostgreSQL, featuring JWT authentication, RESTful API, and Docker containerization.

## 🚀 Features

- **Backend (Django 5.2.11)**
  - RESTful API with Django REST Framework
  - JWT Authentication (Login/Register/Logout)
  - Service Oriented Architecture
  - CRUD operations for Task management
  - PostgreSQL database integration
  - CORS configuration for Angular frontend
  - Admin panel

- **Frontend (Angular 21.1.0)**
  - Standalone components architecture
  - JWT token-based authentication
  - HTTP interceptors for automatic token injection
  - Route guards for protected routes
  - Responsive UI design
  - CRUD operations interface
  - User profile management
  - Dashboard with statistics

- **Database (PostgreSQL 16)**
  - Reliable and scalable database
  - Docker volume for data persistence
  - Health checks

- **Docker**
  - Multi-container setup with Docker Compose
  - Separate containers for frontend, backend, and database
  - Development and production configurations
  - Automatic migrations on startup

## 📋 Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- Git

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd django-angular-crud
```

### 2. Start the Application with Docker

```bash
docker-compose up --build
```

This command will:
- Build all Docker images
- Start PostgreSQL, Django backend, and Angular frontend containers
- Run database migrations
- Collect static files

### 3. Access the Application

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin

### 4. Create a Superuser (Optional)

To access the Django admin panel:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Follow the prompts to create an admin account.

## 🔧 Development Setup (Without Docker)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Update database credentials if needed

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Update API URL** (if needed):
   - Edit `src/environments/environment.ts`
   - Change `apiUrl` to match your backend URL

4. **Run development server:**
   ```bash
   npm start
   ```

5. **Access the application:**
   - Open http://localhost:4200 in your browser

## 📚 API Documentation

### Authentication Endpoints

#### Register
```
POST /api/auth/register/
Body: {
  "username": "string",
  "email": "string",
  "password": "string",
  "password2": "string",
  "first_name": "string" (optional),
  "last_name": "string" (optional)
}
```

#### Login
```
POST /api/auth/login/
Body: {
  "username": "string",
  "password": "string"
}
```

#### Logout
```
POST /api/auth/logout/
Headers: Authorization: Bearer <access_token>
Body: {
  "refresh_token": "string"
}
```

#### Get/Update Profile
```
GET/PATCH /api/auth/profile/
Headers: Authorization: Bearer <access_token>
```

#### Refresh Token
```
POST /api/auth/token/refresh/
Body: {
  "refresh": "string"
}
```

### Task Endpoints

#### List Tasks
```
GET /api/tasks/
Headers: Authorization: Bearer <access_token>
Query params: status, priority, search, ordering
```

#### Create Task
```
POST /api/tasks/
Headers: Authorization: Bearer <access_token>
Body: {
  "title": "string",
  "description": "string",
  "status": "TODO|IN_PROGRESS|DONE",
  "priority": "LOW|MEDIUM|HIGH",
  "due_date": "YYYY-MM-DD" (optional),
  "completed": boolean
}
```

#### Get Task Detail
```
GET /api/tasks/{id}/
Headers: Authorization: Bearer <access_token>
```

#### Update Task
```
PUT/PATCH /api/tasks/{id}/
Headers: Authorization: Bearer <access_token>
```

#### Delete Task
```
DELETE /api/tasks/{id}/
Headers: Authorization: Bearer <access_token>
```

#### Complete Task
```
POST /api/tasks/{id}/complete/
Headers: Authorization: Bearer <access_token>
```

#### Get Statistics
```
GET /api/tasks/statistics/
Headers: Authorization: Bearer <access_token>
```

## 🏗️ Project Structure

```
django-angular-crud/
├── backend/
│   ├── api/                    # Task API app
│   │   ├── models.py           # Task model
│   │   ├── serializers.py      # API serializers
│   │   ├── views.py            # ViewSets
│   │   └── urls.py             # API routes
│   ├── authentication/         # Auth app
│   │   ├── serializers.py      # Auth serializers
│   │   ├── views.py            # Auth views
│   │   └── urls.py             # Auth routes
│   ├── core/                   # Django project settings
│   │   ├── settings.py         # Project settings
│   │   ├── urls.py             # Main URL config
│   │   └── wsgi.py
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/           # Core services, guards, interceptors
│   │   │   │   ├── guards/     # Auth guard
│   │   │   │   ├── interceptors/  # HTTP interceptor
│   │   │   │   ├── models/     # TypeScript interfaces
│   │   │   │   └── services/   # Auth & Task services
│   │   │   ├── features/       # Feature modules
│   │   │   │   ├── auth/       # Login & Register components
│   │   │   │   ├── dashboard/  # Dashboard component
│   │   │   │   ├── tasks/      # Task list & form components
│   │   │   │   └── profile/    # Profile component
│   │   │   ├── shared/         # Shared components
│   │   │   │   └── navbar/     # Navigation bar
│   │   │   ├── app.component.ts
│   │   │   ├── app.config.ts   # App configuration
│   │   │   └── app.routes.ts   # Route definitions
│   │   ├── environments/       # Environment configs
│   │   ├── index.html
│   │   ├── main.ts
│   │   └── styles.css
│   ├── angular.json
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── database/
│   └── init.sql                # PostgreSQL init script
├── docker-compose.yml          # Docker Compose configuration
└── README.md
```

## 🔐 Security Features

- JWT token-based authentication
- Password hashing with Django's built-in system
- HTTP-only token storage
- CORS configuration
- Token refresh mechanism
- Protected API endpoints
- Route guards in Angular

## 🎨 Key Technologies

### Backend
- **Django**: 5.2.11
- **Django REST Framework**: 3.14.0
- **djangorestframework-simplejwt**: 5.3.1
- **django-cors-headers**: 4.3.1
- **psycopg2-binary**: 2.9.9
- **gunicorn**: 21.2.0

### Frontend
- **Angular**: 21.1.0
- **TypeScript**: 5.6.2
- **RxJS**: 7.8.0
- **Standalone Components**: Yes

### Database
- **PostgreSQL**: 16-alpine

### DevOps
- **Docker**: Multi-stage builds
- **Docker Compose**: Service orchestration
- **Nginx**: Frontend reverse proxy

## 📝 Docker Commands

### Start all services
```bash
docker-compose up
```

### Start in detached mode
```bash
docker-compose up -d
```

### Rebuild containers
```bash
docker-compose up --build
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove volumes
```bash
docker-compose down -v
```

### View logs
```bash
docker-compose logs -f
```

### View specific service logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Execute commands in containers
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec db psql -U postgres -d djangodb
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Production Deployment

For production deployment:

1. Update environment variables in `docker-compose.yml` or use `.env` file
2. Change `DEBUG=False` in Django settings
3. Set a strong `SECRET_KEY`
4. Update `ALLOWED_HOSTS`
5. Configure proper CORS settings
6. Use environment-specific database credentials
7. Set up SSL/TLS certificates
8. Use production-grade web server (Nginx/Apache)

## 📄 License

This project is open source and available under the MIT License.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using Django, Angular, and PostgreSQL**