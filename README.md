# Shree Glass Fiber - Backend API

Production-ready FastAPI backend for the Shree Glass Fiber Flutter mobile application.

## Tech Stack

- **Python 3.12** + **FastAPI**
- **SQLAlchemy 2.0** (Async) + **PostgreSQL 16**
- **Alembic** for migrations
- **JWT** authentication (Access + Refresh tokens)
- **Docker** + **Docker Compose**
- **Gunicorn** + **Uvicorn** workers

## Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Make (optional, for shortcut commands)

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env with your values
```

### 2. Start services

```bash
# Using Make
make build
make up

# Or directly
docker compose up -d --build
```

### 3. Run migrations

```bash
make migrate
# Or: docker compose exec app alembic upgrade head
```

### 4. Seed sample data

```bash
make seed
# Or: docker compose exec app python scripts/seed.py
```

### 5. Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## Project Structure

```
app/
├── api/v1/          # API route handlers
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas (request/response)
├── services/        # Business logic
├── repositories/    # Database operations
├── core/            # Security, exceptions, response helpers
├── middleware/      # Custom middleware
├── dependencies/    # FastAPI dependencies (auth guards)
├── config/          # Settings (from .env)
├── database/        # DB session & engine
├── utils/           # Logging, helpers
├── static/          # Static assets
└── uploads/         # User uploads
alembic/             # Database migrations
docker/              # Production configs (nginx, compose override)
tests/               # Unit & integration tests
scripts/             # Seed & utility scripts
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login (email/mobile) |
| POST | `/api/v1/auth/admin/login` | Admin login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout |
| POST | `/api/v1/auth/forgot-password` | Request password reset OTP |
| POST | `/api/v1/auth/reset-password` | Reset password with OTP |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/dashboard` | Dashboard stats |
| GET | `/api/v1/admin/users` | List users (paginated) |
| PUT | `/api/v1/admin/users/{id}/approve` | Approve user |
| PUT | `/api/v1/admin/users/{id}/reject` | Reject user |
| PUT | `/api/v1/admin/users/{id}/suspend` | Suspend user |
| DELETE | `/api/v1/admin/users/{id}` | Soft delete user |
| GET | `/api/v1/admin/audit-logs` | View audit logs |

### CMS
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cms/pages` | All active pages |
| GET | `/api/v1/cms/{slug}` | Page by slug |
| POST | `/api/v1/cms/admin/create` | Create page (admin) |
| PUT | `/api/v1/cms/admin/{id}` | Update page (admin) |
| DELETE | `/api/v1/cms/admin/{id}` | Delete page (admin) |

### Settings & Contact
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/settings` | Get app settings |
| PUT | `/api/v1/settings/admin` | Update settings (admin) |
| GET | `/api/v1/contact` | Get contact info |
| PUT | `/api/v1/contact/admin` | Update contact (admin) |

### Profile & Upload
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/profile` | Get profile |
| PUT | `/api/v1/profile` | Update profile |
| PUT | `/api/v1/profile/change-password` | Change password |
| POST | `/api/v1/upload/image` | Upload image (admin) |
| POST | `/api/v1/upload/pdf` | Upload PDF (admin) |

### Health & Misc
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/ready` | Readiness check |
| GET | `/api/v1/calculation` | Calculation (coming soon) |
| POST | `/api/v1/device-token` | Register FCM token |

## Make Commands

```bash
make help          # Show all commands
make build         # Build containers
make up            # Start services
make down          # Stop services
make logs          # View app logs
make shell         # Open app shell
make db-shell      # Open psql shell
make migrate       # Run migrations
make migrate-create msg="add_field"  # Create migration
make seed          # Seed database
make test          # Run tests
make backup-db     # Backup database
make prod-up       # Start production
```

## Deployment (VPS - Hostinger)

### Optimized for:
- 2 CPU cores
- 8 GB RAM
- Ubuntu Linux
- Docker deployment

### Production deployment:

```bash
# 1. Clone repo on server
# 2. Configure .env with production values
# 3. Start with production compose
docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d

# 4. Run migrations
docker compose exec app alembic upgrade head

# 5. Seed initial data (first time only)
docker compose exec app python scripts/seed.py
```

### Nginx reverse proxy
See `docker/nginx.conf` for the recommended Nginx configuration.

## Super Admin

Admin credentials are stored in `.env`:
```
SUPER_ADMIN_EMAIL=admin@shreeglass.com
SUPER_ADMIN_PASSWORD=SuperAdmin@123
```

Admin is NOT stored in database. Authentication is done against env variables.

## User Flow

1. User registers from Flutter app → Status: **Pending**
2. Admin reviews and approves/rejects
3. Only **Approved** users can login
4. Login returns JWT access + refresh tokens

## License

Proprietary - Shree Glass Fiber Pvt. Ltd.
