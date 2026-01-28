# FastAPI Template

A complete, production-ready template for building modern web applications with FastAPI, including authentication, permission management, real-time WebSockets, and an administrative panel.

## 🚀 Key Features

### **Database and Modeling**
- **FastAPI**: Modern, high-performance web framework for building APIs with Python 3.11+
- **SQLAlchemy**: Powerful ORM with support for both synchronous and asynchronous connections
- **Alembic Migrations**: Database version control system
- **PostgreSQL**: Relational database with full async/sync support
- **Pydantic**: Data validation and automatic serialization

### **Authentication and Security**
- **JWT (JSON Web Tokens)**: Token-based authentication system
- **Refresh Tokens**: Support for session renewal using long-lived tokens (7 days by default)
- **Two-Factor Authentication (2FA/OTP)**: Extra layer of security via Google Authenticator or similar apps
- **OAuth2**: OAuth2 flow implementation with Password Bearer
- **Roles and Permissions System**: Role-Based Access Control (RBAC)
- **Automatic Permission Generation**: Permissions are automatically generated for each endpoint
- **Verification Middleware**: JWT and role verification on every request

### **Real-Time Communication**
- **Socket.IO**: Bi-directional, event-based communication between client and server
- **Asynchronous Events**: `ChannelEvent` system with dependency injection support (`DependsEvent`) and results
- **WebSocket Support**: Full support for WebSocket connections
- **Webhooks System**: Robust incoming and outgoing Webhooks system with automatic logging

### **Extensions and AI** (usage example)
- **AI Agents**: Integration with LangChain and LangGraph for complex logic "example"
- **Agent Architecture**: Support for multi-agent graphs, custom tools, and memory "example"

### **Administrative Panel**
- **Admin Interface**: Web panel to manage API resources
- **Tailwind CSS**: Utility-first CSS framework for custom designs
- **Jinja2 Templates**: Template engine for generating dynamic HTML pages
- **Menu Management**: Role-based dynamic menu system

### **Modular Architecture**
- **Module-based Structure**: Clear and scalable code organization
- **Automatic Route Registration**: Routes are automatically registered following the folder structure
- **Separation of Concerns**: Separate Controllers, Services, Models, and Schemas

### **Code Quality and Type Safety**
- **PEP 561 Compliance**: The project includes `py.typed` markers for full editor and typing tool support
- **Mypy Static Analysis**: Integrated `mypy` configuration to ensure type safety
- **Standard Typing**: Use of `async_sessionmaker[AsyncSession]` and other modern Python types
- **Prometheus**: Integrated application metrics and monitoring
- **APScheduler**: Scheduling of asynchronous tasks and background jobs
- **Redis**: Cache and session storage
- **Nodemon**: Automatic reload during development
- **Docker**: Full containerization with Docker and Docker Compose

## 📁 Project Structure

```
fastapi_template/
├── core/                      # Application core
│   ├── database/             # Database configuration
│   │   ├── drivers/          # Database drivers
│   │   │   └─── postgresql/   # PostgreSQL driver
│   ├── py.typed              # PEP 561 typing marker
│   └── utils/                # Database utilities (pagination, etc.)
│   ├── middlewares/          # Custom middlewares
│   │   ├── jwt_verify.py         # JWT token verification
│   │   └── role_verify.py        # Role-based permission verification
│   ├── jobs/                 # Tasks scheduled with APScheduler
│   ├── routes/               # Main routes configuration
│   ├── services/             # Shared services
│   ├── schemas/              # Shared Pydantic schemas
│   ├── cache/                # Cache system with Redis
│   ├── event/                # Custom event system
│   └── utils/                # General utilities
│
├── app/                       # Main application directory
│   ├── modules/               # Functional modules
│   │   ├── auth/             # Authentication (sign-in, sign-up)
│   │   ├── users/            # User management
│   │   ├── roles/            # Role management
│   │   ├── permissions/      # Permission management
│   │   ├── tokens/           # API token management
│   │   └── menu/             # Dynamic menu system
│   │
│   ├── sockets/               # WebSockets and Socket.IO
│   │   ├── __init__.py       # Socket.IO event initialization
│   │   └── live/             # Real-time events
│   │
│   └── public/                # Static public files
│
├── admin/                     # Administrative panel
│   ├── src/                  # Jinja2 templates
│   ├── static/               # Static files (CSS, JS, images)
│   ├── templates/            # Template configuration
│   └── global/               # Global admin configuration
├── logs/                      # Log files
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yaml        # Service orchestration
├── .env.example              # Environment variables example
└── ER_db_diagram.dbml        # Database diagram
```

## 🛠️ CLI - Module Generator

This project includes a **CLI tool** to automatically generate modules with all the necessary structure.

### Using the Generator

**Generate a simple module:**
```bash
python cli.py generate:module products
```

This creates:
```
app/modules/products/
├── __init__.py
├── controller.py    # FastAPI Router with CRUD endpoints
├── schemas.py       # Pydantic Schemas (Request/Response)
├── models.py        # SQLAlchemy Model
└── services.py      # Business Logic
```

**Generate nested modules:**
```bash
python cli.py generate:module store.inventory
```

This creates:
```
app/modules/store/
├── __init__.py
└── inventory/
    ├── __init__.py
    ├── controller.py
    ├── schemas.py
    ├── models.py
    └── services.py
```

### Generated Files

Each generated module includes:

- **controller.py**: Full Router with CRUD endpoints (GET, POST, PUT, DELETE)
- **schemas.py**: Request/Response Schemas with pagination
- **models.py**: SQLAlchemy Model with basic fields
- **services.py**: Base service functions

### Post-Generation Customization

After generating a module:

1. **Edit `models.py`**: Add your model's specific fields
2. **Update `schemas.py`**: Add necessary validations and fields
3. **Modify `controller.py`**: Customize endpoints to your needs
4. **Implement `services.py`**: Add specific business logic
5. **Register the router**: Import and register in `main.py` or use auto-registration
6. **Run migrations**: Create and apply Alembic migrations if you modified models

## 🛠️ Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 12 or higher
- Node.js and npm (for frontend development)
- Redis (optional, for cache)
- Docker and Docker Compose (optional)

### Option 1: Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/TheGuyInTheShell/fastapi-template.git
cd fastapi-template
```

2. **Create and configure the virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Node.js dependencies** (for Tailwind CSS)
```bash
npm install
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

### **Database Migrations**
This project uses **Alembic** to manage database schema changes.

#### Useful Commands:
- **Generate a new migration automatically**:
  ```bash
  alembic revision --autogenerate -m "change description"
  ```
- **Apply migrations to the database**:
  ```bash
  alembic upgrade head
  ```
- **Revert the last migration**:
  ```bash
  alembic downgrade -1
  ```
- **View migration history**:
  ```bash
  alembic history --verbose
  ```

Alembic configurations are found in `alembic.ini` and `migrations/env.py`. The system automatically loads the connection from your `.env` file.

`.env` file configuration:
```env
# JWT Configuration
JWT_KEY=your_jwt_secret_key_here
JWT_ALG=HS256

# Database Configuration
DB_NAME=database_name
DB_USER=postgres_user
DB_PASSWORD=postgres_password
DB_HOST=localhost
DB_PORT=5432

# Application Mode
MODE=DEBUG  # or PRODUCTION
```

6. **Create the database**
```bash
# Connect to PostgreSQL and create the database
psql -U postgres
CREATE DATABASE database_name;
```

### Option 2: Installation with Docker

1. **Clone the repository**
```bash
git clone https://github.com/TheGuyInTheShell/fastapi-template.git
cd fastapi-template
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env as needed
```

3. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8880`

To enable AI agents, make sure to configure the necessary API keys in `.env`:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

## 🚀 Usage

### Development

**Start the development server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Compile Tailwind CSS in watch mode:**
```bash
nodemon
```

**Access interactive documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Prometheus Metrics: `http://localhost:8000/metrics`

### Production

**With Gunicorn:**
```bash
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --workers 4
```

**With PM2 (using ecosystem.config.js):**
```bash
pm2 start ecosystem.config.js
```

**With Docker:**
```bash
docker-compose up -d
```

### Static Type Analysis

The project uses `mypy` to ensure type safety. To run the analysis:

```bash
python -m mypy .
```

The configuration is in `mypy.ini`, which automatically excludes admin templates to avoid module name collisions in controllers.

## 📚 Modules and Features

### 1. **Authentication Module** (`modules/auth/`)

Manages user registration and login.

**Endpoints:**
- `POST /auth/sign-up` - Register new user
- `POST /auth/sign-in` - Login and obtain JWT token
- `GET /auth/` - Verify token

**Features:**
- Password encryption with bcrypt
- JWT token generation with configurable expiration
- Credential validation
- Duplicate user prevention
- **Refresh Tokens**: `/auth/refresh` endpoint to obtain new access tokens without re-authenticating
- **2FA/OTP**: Support for two-factor authentication via:
    - `GET /auth/2fa/setup` - Generates secret and QR code
    - `POST /auth/2fa/enable` - Enables 2FA for the user
    - `POST /auth/verify-otp` - Verifies OTP code during login
    - `POST /auth/2fa/disable` - Disables 2FA

### 2. **Users Module** (`modules/users/`)

Full system user management.

**Endpoints:**
- `GET /users/me` - Get authenticated user data
- `GET /users/` - List all users (with pagination)
- `GET /users/id/{id}` - Get user by ID
- `PUT /users/id/{id}` - Update user
- `DELETE /users/id/{id}` - Delete user

**Features:**
- Automatic pagination
- Filtering and searching
- Role relationship
- Data validation with Pydantic

### 3. **Roles Module** (`modules/roles/`)

Role system for access control.

**Endpoints:**
- `GET /roles/` - List roles
- `GET /roles/id/{id}` - Get role by ID
- `POST /roles/` - Create new role
- `PUT /roles/id/{id}` - Update role
- `DELETE /roles/id/{id}` - Delete role

**Features:**
- Hierarchical roles
- Permission assignment to roles
- Many-to-many relationship with permissions

### 4. **Permissions Module** (`modules/permissions/`)

Granular permission management.

**Endpoints:**
- `GET /permissions/` - List permissions
- `GET /permissions/id/{id}` - Get permission by ID
- `POST /permissions/` - Create permission
- `PUT /permissions/id/{id}` - Update permission
- `DELETE /permissions/id/{id}` - Delete permission

**Features:**
- **Automatic generation**: Permissions are automatically created at application startup based on registered routes
- Access control per endpoint
- Flexible assignment to roles

### 5. **API Tokens Module** (`modules/tokens/`)

API token management for integrations.

**Endpoints:**
- `GET /tokens/` - List tokens
- `GET /tokens/id/{id}` - Get token by ID
- `POST /tokens/` - Create new token
- `PUT /tokens/id/{id}` - Update token
- `DELETE /tokens/id/{id}` - Delete token

### 6. **Menus Module** (`modules/menu/`)

Dynamic role-based menu system.

**Endpoints:**
- `GET /menu/` - List menus
- `GET /menu/id/{id}` - Get menu by ID
- `POST /menu/` - Create menu
- `PUT /menu/id/{id}` - Update menu
- `DELETE /menu/id/{id}` - Delete menu

**Features:**
- Hierarchical menus (parents and children)
- Role assignment
- Custom icons and ordering

### 7. **WebSockets and Socket.IO** (`sockets/`)

Real-time communication.

**Features:**
- Custom events
- Rooms and namespaces
- Connection authentication
- Message broadcast
- FastAPI integration

**Usage Example:**
```python
# Server (sockets/live/events.py)
@sio.on('message')
async def handle_message(sid, data):
    await sio.emit('response', {'data': 'received'}, room=sid)
```

### 8. **Cache System** (`core/cache/`)

Redis-based cache to improve performance.

**Features:**
- Caching of frequent queries
- Configurable TTL
- Cache invalidation

### 9. **Scheduled Tasks** (`core/jobs/`)

Background task execution with APScheduler.

**Features:**
- Cron tasks
- Interval tasks
- One-time tasks
- Lifecycle management

### 10. **Webhooks System** (`app/webhooks/`)

Centralized system for handling incoming and outgoing webhooks.

**Structure:**
- `in/`: Controllers for receiving webhooks from external services.
- `out/`: Subscribers listening for internal events and sending data to external services.

**Features:**
- **Auto-discovery**: Controllers and subscribers are automatically loaded.
- **Integrated ChannelEvent**: Full decoupling via events.
- **Validation**: Pydantic used to validate incoming payloads.

### 11. **Extensions and AI** (`app/ext/`)

Folder dedicated to complex business logic and AI agents.

**Structure (`app/ext/ia/`):**
- `agents/`: Agent definitions (Researcher, Writer, etc.)
- `graphs/`: Workflows with LangGraph (StateGraph, MultiAgentGraph)
- `tools/`: Custom tools for agents
- `chains/`: LangChain processing chains

**Usage Example (LangGraph):**
The system includes a multi-agent graph example where a researcher and a writer collaborate to generate content.

## 🔧 Architecture and Patterns

### Modular Architecture

Each module follows a consistent structure:

```
module_name/
├── controller.py    # Endpoints and routes
├── services.py      # Business logic
├── models.py        # Database models
└── schemas.py       # Pydantic schemas (validation)
```

### Automatic Route Registration

Routes are automatically registered based on the folder structure:

```python
# core/utils/import_modules.py analyzes the modules/ folder
# and automatically registers all found routers
```

### Middleware Pipeline

1. **CORS Middleware**: Allowed origins configuration
2. **JWT Verify**: Token validation on protected routes
3. **Role Verify**: Role-based permission verification

### Database Connections

**Asynchronous** (recommended for endpoints):
```python
from core.database import get_async_db

@router.get("/")
async def endpoint(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

**Synchronous** (for initialization):
```python
from core.database.sync_connection import engineSync
BaseSync.metadata.create_all(engineSync)
```

### Event System (ChannelEvent)

The core of asynchronous communication is `ChannelEvent`, which allows:

1. **Subscribe/Listen**: `@channel.subscribe_to` and `@channel.listen_to` decorators.
2. **Dependency Injection**: Use of `result = channel.DependsEvent(event_result)` to receive results from previous events.
3. **Smart Injection**: Subscribers automatically receive the `result` argument if declared in their signature.
4. **Resilience**: Robust event initialization and error handling.

## 🔐 Security

### Implemented Best Practices

1. **Hashed Passwords**: Use of bcrypt for secure hashing
2. **JWT with Expiration**: Tokens with limited lifespan
3. **Configured CORS**: Control over allowed origins
4. **Input Validation**: Pydantic validates all input data
5. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injections
6. **Environment Variables**: Sensitive credentials in .env files

### Generate Secure JWT Key

```python
import secrets
jwt_key = secrets.token_hex(32)
print(jwt_key)
```

## 📊 Database

### Main Models

- **User**: System users
- **Role**: User roles
- **Permission**: Granular permissions
- **Menu**: Menu elements
- **MenuRole**: Menu-role relationship
- **ApiToken**: API tokens

### Migrations

The project creates tables automatically upon startup:

```python
# In main.py
BaseSync.metadata.create_all(engineSync)
BaseAsync.metadata.create_all(engineSync)
```

For more advanced migrations, consider using **Alembic**:

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 🎨 Administrative Panel

The administrative panel includes:

- **Dashboard**: System overview
- **User Management**: Full CRUD
- **Roles and Permissions Management**: Visual assignment
- **Menu Configuration**: Menu editor
- **Logs and Monitoring**: Log visualization

**Access**: `http://localhost:8000/admin`

## 📈 Monitoring and Metrics

### Prometheus

Metrics available at `/metrics`:

- Number of requests
- Response latency
- HTTP errors
- Resource usage

### Grafana Integration

```yaml
# Example configuration for Grafana
datasources:
  - name: Prometheus
    type: prometheus
    url: http://localhost:8000/metrics
```

## 🧪 Testing

### Test Structure (Recommended)

```
tests/
├── test_auth.py
├── test_users.py
├── test_roles.py
└── conftest.py
```

### Test Example

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_sign_up():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/sign-up", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 201
```

## 🌐 Deployment

### Production Environment Variables

```env
MODE=PRODUCTION
JWT_KEY=super_secure_production_key
DB_HOST=db.production.com
DB_PASSWORD=secure_password
```

### Nginx as Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /sio/ {
        proxy_pass http://localhost:8000/sio/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Systemd Service

```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/fastapi_template
ExecStart=/path/to/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## 📞 Support

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Socket.IO Documentation**: https://socket.io/docs/
- **Repository**: https://github.com/TheGuyInTheShell/fastapi-template

## 🎯 Upcoming Features

- [ ] SMTP Connection
- [ ] Per-user rate limiting
- [ ] Full Tests
- [ ] Multi-language support (i18n)

---

**Developed with ❤️ using FastAPI**
