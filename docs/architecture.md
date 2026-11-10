# Django Calculator Architecture Documentation

## Overview

The Django Calculator is a secure, production-ready web application built with Django 5.1. It follows a clean architecture pattern with separation of concerns between the web layer (views), business logic layer (services), and data access layer (repositories).

## Architecture Patterns

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Views     │  │    Forms    │  │      Templates      │  │
│  │  (Django)   │  │  (Django)   │  │    (HTML/CSS/JS)    │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘  │
└─────────┼────────────────┼──────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              CalculationService                         │ │
│  │         (Pure Python, No Django Dependencies)          │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    DTOs     │  │  Exceptions │  │   Validators        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Access Layer                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           CalculationRequestRepository                  │ │
│  │              (Repository Pattern)                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Django ORM Models                          │ │
│  │         (CalculationRequest, OperationType)              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database Layer                          │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │   SQLite        │  │         PostgreSQL 16           │  │
│  │ (Development)   │  │         (Production)            │  │
│  └─────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Security Gates

The following security gates are enforced in CI/CD and must pass before deployment:

#### 1. eval()/exec() Prohibition Gate

**Command:**
```bash
grep -rn 'eval\|exec(' --include='*.py' ./calculator ./health ./calculator_project 2>/dev/null || echo "No eval/exec found - PASS"
```

**Expected Result:** Zero matches in application code.

**Rationale:** Dynamic code execution via `eval()` or `exec()` is a critical security vulnerability that can lead to Remote Code Execution (RCE). The calculator uses an explicit operator dispatch table in `calculator/services.py`:

```python
if operation == OPERATION_ADD:
    return operand_a + operand_b
elif operation == OPERATION_SUBTRACT:
    return operand_a - operand_b
elif operation == OPERATION_MULTIPLY:
    return operand_a * operand_b
elif operation == OPERATION_DIVIDE:
    if operand_b == Decimal('0'):
        raise DivisionByZeroError()
    return operand_a / operand_b
```

#### 2. SECRET_KEY Environment Enforcement Gate

**Verification:**
```bash
grep -n "SECRET_KEY" calculator_project/settings.py | grep -v "os.environ" | grep -v "^#"
```

**Expected Result:** No hardcoded SECRET_KEY values.

**Implementation:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY environment variable is required."
    )
```

#### 3. Security Headers Verification

**Production Security Headers:**
- `SECURE_SSL_REDIRECT=True` - Redirects all HTTP to HTTPS
- `SECURE_HSTS_SECONDS=31536000` - HTTP Strict Transport Security (1 year)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS=True` - HSTS applies to subdomains
- `SECURE_HSTS_PRELOAD=True` - Allow browser preload lists
- `CSRF_COOKIE_SECURE=True` - CSRF cookie only sent over HTTPS
- `SESSION_COOKIE_SECURE=True` - Session cookie only sent over HTTPS
- `CSRF_COOKIE_HTTPONLY=True` - CSRF cookie not accessible via JavaScript
- `SESSION_COOKIE_HTTPONLY=True` - Session cookie not accessible via JavaScript
- `SECURE_CONTENT_TYPE_NOSNIFF=True` - Prevent MIME type sniffing
- `SECURE_BROWSER_XSS_FILTER=True` - Enable browser XSS filter
- `X_FRAME_OPTIONS='DENY'` - Prevent clickjacking

### Input Validation Architecture

1. **Form Layer** (`calculator/forms.py`):
   - DecimalField validation with range constraints
   - ChoiceField whitelisting for operations
   - Custom clean methods for business rule validation

2. **Service Layer** (`calculator/services.py`):
   - Explicit operation whitelist
   - Division by zero protection
   - Overflow detection (results > 1e30)
   - Decimal quantization for precision control

3. **Database Layer** (`calculator/models.py`):
   - DecimalField with precision limits
   - Null constraints where appropriate

## Database Architecture

### Dual-Mode Persistence

The application supports seamless switching between SQLite (development) and PostgreSQL (production) via environment configuration:

```python
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

### Connection Pooling

- `conn_max_age=600` - Keep connections alive for 10 minutes
- `conn_health_checks=True` - Verify connections before reuse

## Deployment Architecture

### Container Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Container                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Multi-stage Build: builder → production                │ │
│  │                                                         │ │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │ │
│  │  │   Nginx     │ or │  AWS ALB    │ or │  Azure LB   │  │ │
│  │  │  (Reverse   │    │  (L7 Load   │    │  (L7 Load   │  │ │
│  │  │   Proxy)    │    │  Balancer)  │    │  Balancer)  │  │ │
│  │  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │ │
│  │         │                  │                  │         │ │
│  │         └──────────────────┼──────────────────┘         │ │
│  │                            ▼                           │ │
│  │                   ┌─────────────────┐                    │ │
│  │                   │   Gunicorn      │                    │ │
│  │                   │   (WSGI Server) │                    │ │
│  │                   │   - Workers: 2+                   │ │
│  │                   │   - Timeout: 30s                  │ │ │
│  │                   └────────┬────────┘                    │ │
│  │                            │                           │ │
│  │                   ┌────────▼────────┐                    │ │
│  │                   │     Django      │                    │ │
│  │                   │   Application   │                    │ │
│  │                   └─────────────────┘                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Gunicorn Configuration

- **Workers:** `(2 * CPU cores) + 1` (auto-detected)
- **Worker Class:** `sync` (recommended for Django)
- **Timeout:** 30 seconds
- **Keepalive:** 2 seconds
- **Bind:** `0.0.0.0:8000`

### Health Checks

The application exposes a health check endpoint at `/health/`:

```python
# health/views.py
class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
        })
```

Docker health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1
```

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.12+ |
| Framework | Django | 5.1.x |
| WSGI Server | Gunicorn | 22.x |
| Database (Dev) | SQLite | 3.x |
| Database (Prod) | PostgreSQL | 16.x |
| Container | Docker | Latest |
| Orchestration | Docker Compose | Latest |

## File Organization

```
django-calculator/
├── calculator/                 # Main application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── dtos.py                 # Data Transfer Objects
│   ├── exceptions.py           # Domain exceptions
│   ├── forms.py                # Form validation
│   ├── models.py               # Database models
│   ├── repositories.py         # Data access layer
│   ├── services.py             # Business logic
│   ├── urls.py                 # App URL routing
│   └── views.py                # HTTP request handlers
├── calculator_project/         # Project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL routing
│   └── wsgi.py                 # WSGI entry point
├── health/                     # Health check app
│   ├── __init__.py
│   ├── urls.py
│   └── views.py
├── docs/                       # Documentation
│   ├── architecture.md         # This file
│   └── setup.md                # Setup instructions
├── static/                     # Static assets
│   └── css/
├── templates/                  # HTML templates
│   ├── base.html
│   └── calculator/
├── tests/                      # Test suite
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Base compose config
├── docker-compose.override.yml # PostgreSQL override
├── gunicorn.conf.py            # Gunicorn configuration
├── manage.py                   # Django management
├── requirements.in             # Prod dependencies (source)
├── requirements.txt            # Prod dependencies (locked)
├── requirements-dev.in         # Dev dependencies (source)
├── requirements-dev.txt        # Dev dependencies (locked)
└── .env.example                # Environment template
```

## Performance Considerations

1. **Static Files:** Collected at build time, served by reverse proxy
2. **Database Connections:** Pooled with health checks
3. **Gunicorn Workers:** Auto-scaled based on CPU cores
4. **Decimal Arithmetic:** Using Python's `decimal.Decimal` for precision
5. **Template Caching:** Enabled in production

## Monitoring & Observability

- **Logs:** Structured logging to stdout (captured by container runtime)
- **Health Endpoint:** `/health/` for load balancer health checks
- **Gunicorn Access Logs:** Configured in `gunicorn.conf.py`
- **Django Logging:** Configured in `settings.py`
