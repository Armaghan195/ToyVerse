# ToyVerse Backend API

A comprehensive FastAPI-based e-commerce backend demonstrating Object-Oriented Programming (OOP) principles with SQL Server integration.

## 📋 Table of Contents

- [Overview](#overview)
- [OOP Principles Demonstrated](#oop-principles-demonstrated)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Database Schema](#database-schema)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Running the Application](#running-the-application)
- [Testing](#testing)

---

## 🎯 Overview

ToyVerse Backend is a RESTful API built with **FastAPI** and **SQL Server** (SSMS) that powers an e-commerce toy store. This project demonstrates key OOP concepts including:

- ✅ **Abstraction**
- ✅ **Encapsulation**
- ✅ **Inheritance**
- ✅ **Polymorphism**
- ✅ **Low Coupling**
- ✅ **High Cohesion**

---

## 🏛️ OOP Principles Demonstrated

### 1. ABSTRACTION

**Location**: `app/repositories/base_repository.py`, `app/services/base_service.py`

Abstract base classes define contracts that concrete implementations must follow:

```python
class BaseRepository(ABC, Generic[T]):
    """Abstract repository defining data access contract"""

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID - MUST be implemented by children"""
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """Create entity - MUST be implemented by children"""
        pass
```

**Benefits**:
- Forces consistent interface across all repositories
- Defines clear contract for data access operations
- Prevents instantiation of incomplete implementations

### 2. ENCAPSULATION

**Location**: `app/core/security.py`, `app/models/product.py`

Data and methods are bundled together with controlled access:

```python
class PasswordHandler:
    """Encapsulates password hashing logic"""

    def __init__(self):
        # PRIVATE attribute - cannot be accessed directly
        self._pwd_context = CryptContext(schemes=["bcrypt"])

    def hash_password(self, password: str) -> str:
        """PUBLIC method - controlled access to hashing"""
        return self._pwd_context.hash(password)
```

**Benefits**:
- Hides implementation details
- Provides controlled access through public methods
- Protects sensitive data (passwords never stored in plain text)

### 3. INHERITANCE

**Location**: `app/models/user.py`, `app/models/base.py`

Child classes inherit properties and methods from parent classes:

```python
class BaseModel:
    """Base class for all models"""
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(BaseModel):
    """Inherits id and created_at from BaseModel"""
    username = Column(String(50))
    # Automatically has id and created_at

class Admin(User):
    """Inherits everything from User AND BaseModel"""
    # Gets username, id, created_at automatically
```

**Benefits**:
- Code reuse (DRY - Don't Repeat Yourself)
- Establishes "is-a" relationships
- Consistent structure across models

### 4. POLYMORPHISM

**Location**: `app/models/user.py`

Different classes can be used interchangeably through a common interface:

```python
class User(BaseModel):
    def get_permissions(self) -> List[str]:
        """Base implementation"""
        return ["read"]

class Admin(User):
    def get_permissions(self) -> List[str]:
        """DIFFERENT implementation for Admin"""
        return ["read", "write", "delete", "manage_users"]

class Customer(User):
    def get_permissions(self) -> List[str]:
        """DIFFERENT implementation for Customer"""
        return ["read", "manage_cart", "place_orders"]

# Polymorphism in action:
def check_access(user: User, action: str) -> bool:
    # Works with Admin, Customer, or any User subclass!
    return action in user.get_permissions()
```

**Benefits**:
- Same interface, different behavior
- Flexible and extensible code
- Runtime behavior based on actual object type

### 5. LOW COUPLING

**Location**: `app/services/product_service.py`, `app/api/dependencies.py`

Components are loosely connected through abstractions (Dependency Injection):

```python
class ProductService:
    """Service depends on ABSTRACTION, not implementation"""

    def __init__(self, repository: BaseRepository[Product]):
        # Depends on interface, not ProductRepository specifically
        self._repository = repository

    def get_by_id(self, id: int):
        # Service doesn't know HOW repository gets data
        # Only knows THAT it can get data
        return self._repository.get_by_id(id)
```

**Benefits**:
- Easy to swap implementations
- Changes in one module don't affect others
- Better testability (can mock dependencies)

### 6. HIGH COHESION

**Location**: All service and repository modules

Each class has a single, well-defined responsibility:

```python
# HIGH COHESION - ProductService ONLY handles product business logic
class ProductService:
    def get_by_id(self, id: int): ...
    def create(self, data: dict): ...
    def update(self, id: int, data: dict): ...
    # All methods relate to products ONLY

# DIFFERENT responsibility - AuthService ONLY handles authentication
class AuthService:
    def register(self, user_data): ...
    def authenticate(self, username, password): ...
    def create_token(self, user): ...
    # All methods relate to authentication ONLY
```

**Benefits**:
- Easy to understand and maintain
- Changes are localized
- Better reusability

---

## 🏗️ Architecture

The application follows a **Layered Architecture with Repository Pattern**:

```
┌─────────────────────────────────────────┐
│         API Layer (Routes)              │  ← HTTP Endpoints
│         app/api/routes/                 │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Service Layer (Business Logic)     │  ← ENCAPSULATION
│         app/services/                   │     HIGH COHESION
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│    Repository Layer (Data Access)       │  ← LOW COUPLING
│         app/repositories/               │     ABSTRACTION
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Database (SQL Server)              │  ← PERSISTENCE
│         ToyVerseDB                      │
└─────────────────────────────────────────┘
```

**Key Points**:
- **Routes** handle HTTP requests/responses
- **Services** contain business logic and validation
- **Repositories** encapsulate all database operations
- **Models** define database structure (ORM)
- **Schemas** validate request/response data (Pydantic)

---

## 🛠️ Technologies

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework for building APIs |
| **SQLAlchemy** | ORM for database operations |
| **Pydantic** | Data validation and settings |
| **SQL Server** | Database (SSMS with Windows Authentication) |
| **PyODBC** | SQL Server driver |
| **Python-Jose** | JWT token handling |
| **Passlib** | Password hashing (bcrypt) |
| **Uvicorn** | ASGI server |

---

## 💾 Database Schema

### SQL Server Connection

- **Server**: `ZOHAD\SQLEXPRESS`
- **Database**: `ToyVerseDB`
- **Authentication**: Windows Authentication
- **Driver**: ODBC Driver 17 for SQL Server

### Tables

#### Users Table
```sql
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) NOT NULL,  -- 'admin' or 'customer'
    full_name NVARCHAR(100),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
)
```

**POLYMORPHISM**: User table with polymorphic identity:
- `role = 'admin'` → Admin instance
- `role = 'customer'` → Customer instance

#### Products Table
```sql
CREATE TABLE products (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category NVARCHAR(50) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    rating INT DEFAULT 0,
    icon NVARCHAR(10),
    images_json NVARCHAR(MAX),  -- JSON array of image URLs
    description NVARCHAR(MAX),
    detailed_description NVARCHAR(MAX),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
)
```

#### Cart Items Table
```sql
CREATE TABLE cart_items (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    product_id INT NOT NULL FOREIGN KEY REFERENCES products(id),
    quantity INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
)
```

#### Orders Table
```sql
CREATE TABLE orders (
    id INT IDENTITY(1,1) PRIMARY KEY,
    order_number NVARCHAR(50) UNIQUE NOT NULL,
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    customer_details_json NVARCHAR(MAX) NOT NULL,
    items_json NVARCHAR(MAX) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    payment_method NVARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
)
```

#### Reviews Table
```sql
CREATE TABLE reviews (
    id INT IDENTITY(1,1) PRIMARY KEY,
    product_id INT NOT NULL FOREIGN KEY REFERENCES products(id),
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(id),
    rating INT NOT NULL,
    text NVARCHAR(MAX),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL DEFAULT GETDATE()
)
```

---

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **SQL Server** (SSMS) installed
3. **ODBC Driver 17 for SQL Server** installed
4. **Windows Authentication** configured for SQL Server

### Step 1: Clone and Navigate

```bash
cd ToyVerse-main/ToyVerse-Backend
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Edit `.env` and update settings:
```env
DB_SERVER=ZOHAD\SQLEXPRESS
DB_NAME=ToyVerseDB
SECRET_KEY=your-secret-key-here  # Generate using: openssl rand -hex 32
GROQ_API_KEY=your-groq-api-key   # Get from https://console.groq.com
```

### Step 5: Initialize Database

```bash
python scripts/init_db.py
```

This will:
- Create `ToyVerseDB` database if it doesn't exist
- Create all tables (users, products, cart_items, orders, reviews)
- Verify table creation

### Step 6: Seed Initial Data

```bash
python scripts/seed_data.py
```

This will create:
- **Admin user**: username=`admin`, password=`admin123`
- **Test customer**: username=`customer`, password=`customer123`
- **12 sample products** from the frontend

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000
```

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login with credentials | No |
| POST | `/api/auth/logout` | Logout current user | Yes |
| GET | `/api/auth/me` | Get current user info | Yes |

#### Example: Register
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "customer"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "customer",
    "permissions": ["read", "manage_cart", "place_orders", "write_reviews"]
  }
}
```

### Product Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/products` | Get all products (with filters) | No |
| GET | `/api/products/{id}` | Get product by ID | No |
| POST | `/api/products` | Create product | Yes (Admin) |
| PUT | `/api/products/{id}` | Update product | Yes (Admin) |
| DELETE | `/api/products/{id}` | Delete product | Yes (Admin) |

#### Example: Get Products with Filters
```bash
GET /api/products?category=Sets&price_max=50&rating=4&in_stock=true

Response:
[
  {
    "id": 1,
    "title": "Avengers Tower",
    "price": 40.99,
    "category": "Sets",
    "stock": 10,
    "rating": 5,
    "icon": "🏢",
    "is_in_stock": true,
    "formatted_price": "$40.99",
    "images": ["https://..."],
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎮 Running the Application

### Development Mode

```bash
python -m app.main
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify It's Running

1. Open browser: http://localhost:8000
2. Should see: `{"message": "Welcome to ToyVerse API"}`
3. Check health: http://localhost:8000/health

---

## 🧪 Testing

### Manual Testing with Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Testing Authentication Flow

1. **Register** a new user via `/api/auth/register`
2. **Login** with credentials via `/api/auth/login`
3. Copy the `access_token` from response
4. Click **"Authorize"** button (top right in Swagger UI)
5. Enter: `Bearer <your-token>`
6. Now you can access protected endpoints

### Testing Admin Endpoints

1. Login as admin:
```json
{
  "username": "admin",
  "password": "admin123"
}
```
2. Use the admin token to create/update/delete products

---

## 📂 Project Structure

```
ToyVerse-Backend/
│
├── app/
│   ├── api/                      # API Layer
│   │   ├── routes/
│   │   │   ├── auth.py          # Authentication routes
│   │   │   └── products.py      # Product routes
│   │   └── dependencies.py      # Dependency injection
│   │
│   ├── services/                 # Business Logic Layer
│   │   ├── base_service.py      # ABSTRACTION - Base service
│   │   ├── auth_service.py      # Authentication logic
│   │   └── product_service.py   # Product logic
│   │
│   ├── repositories/             # Data Access Layer
│   │   ├── base_repository.py   # ABSTRACTION - Base repository
│   │   ├── user_repository.py   # User data access
│   │   └── product_repository.py # Product data access
│   │
│   ├── models/                   # Database Models (ORM)
│   │   ├── base.py              # INHERITANCE - Base model
│   │   ├── user.py              # POLYMORPHISM - User/Admin/Customer
│   │   ├── product.py           # Product model
│   │   ├── cart.py              # Cart item model
│   │   ├── order.py             # Order model
│   │   └── review.py            # Review model
│   │
│   ├── schemas/                  # Pydantic Schemas
│   │   ├── user.py              # ENCAPSULATION - User validation
│   │   └── product.py           # Product validation
│   │
│   ├── core/                     # Core Configuration
│   │   ├── config.py            # ENCAPSULATION - Settings
│   │   ├── database.py          # Database connection
│   │   └── security.py          # ENCAPSULATION - Security utils
│   │
│   ├── utils/
│   │   └── logger.py            # Logging utilities
│   │
│   └── main.py                   # FastAPI application
│
├── scripts/
│   ├── init_db.py               # Database initialization
│   └── seed_data.py             # Seed initial data
│
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

---

## 🎓 OOP Concepts Summary

### Where to Find Each Concept

| Concept | File | Lines/Classes |
|---------|------|---------------|
| **ABSTRACTION** | `app/repositories/base_repository.py` | `BaseRepository` class (lines 20-75) |
| **ABSTRACTION** | `app/services/base_service.py` | `BaseService` class (lines 15-120) |
| **ENCAPSULATION** | `app/core/security.py` | `PasswordHandler`, `JWTHandler` classes |
| **ENCAPSULATION** | `app/models/product.py` | `@property` decorators for images, stock |
| **INHERITANCE** | `app/models/base.py` | `BaseModel` → all models inherit |
| **INHERITANCE** | `app/models/user.py` | `User` → `Admin`, `Customer` |
| **POLYMORPHISM** | `app/models/user.py` | `get_permissions()` method override |
| **LOW COUPLING** | `app/services/` | Services depend on repository abstraction |
| **HIGH COHESION** | All service files | Each service handles single responsibility |

---

## 🔐 Security Features

1. **Password Hashing**: Bcrypt algorithm (never stores plain passwords)
2. **JWT Authentication**: Secure token-based authentication
3. **Role-Based Access Control**: Admin vs Customer permissions
4. **SQL Injection Prevention**: SQLAlchemy ORM (parameterized queries)
5. **CORS Configuration**: Controlled cross-origin requests

---

## 🚧 Future Enhancements (Phase 2-4)

- [ ] Cart management endpoints
- [ ] Order processing system
- [ ] Product reviews API
- [ ] Chatbot integration (Groq AI)
- [ ] Image upload functionality
- [ ] Activity logging
- [ ] Admin analytics dashboard
- [ ] Email notifications
- [ ] Payment gateway integration

---

## 📞 Support

For issues or questions:
1. Check the code comments (extensive documentation)
2. Review this README
3. Check SQL Server connection settings
4. Verify ODBC Driver 17 is installed

---

## 👨‍💻 Author

Created as a demonstration of OOP principles in a real-world FastAPI application with SQL Server.

---

## 📝 License

This project is for educational purposes.

---

**Happy Coding! 🚀**
