# Django Calculator

A secure, production-ready calculator web application built with Django 5.1.

## Features

- **Secure by Design**: No `eval()`/`exec()` - uses explicit operator dispatch
- **Dual Database**: SQLite for development, PostgreSQL for production
- **Production Ready**: Gunicorn WSGI server with optimized configuration
- **Containerized**: Docker and Docker Compose support
- **Health Checks**: Built-in health endpoint for monitoring
- **Decimal Precision**: High-precision arithmetic using Python's `decimal.Decimal`

## Quick Start

### Using Docker (Recommended)

```bash
# Clone and enter directory
cd django-calculator

# Copy environment template
cp .env.example .env
# Edit .env and set SECRET_KEY

# Run with SQLite (default)
docker compose up --build

# Or run with PostgreSQL (production-like)
docker compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

Access the application at http://localhost:8000/

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env
# Edit .env and set SECRET_KEY

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start development server
python manage.py runserver
```

## ⚠️ Development Server Boundary

**`manage.py runserver` is a single-threaded development server. It MUST NOT be used in production or demo environments exposed beyond localhost. Use Gunicorn (included in requirements.txt) for all production-equivalent deployments.**

For production, use:
```bash
gunicorn calculator_project.wsgi:application --config gunicorn.conf.py
```

Or deploy using the provided Dockerfile which uses Gunicorn by default.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Views     │────▶│   Forms     │────▶│  Service    │
│  (Django)   │     │ (Validation)│     │ (Business)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │  Repository │
                                        │   (ORM)     │
                                        └──────┬──────┘
                                               │
                                        ┌──────▼──────┐
                                        │  Database   │
                                        │SQLite/PostgreSQL
                                        └─────────────┘
```

## Security Features

- **No Dynamic Code Execution**: Explicit operator dispatch table, no `eval()`/`exec()`
- **Environment-Based Secrets**: `SECRET_KEY` must be set via environment variable
- **Security Headers**: HSTS, XSS Protection, Content Type Nosniff, Frame Options
- **CSRF Protection**: All POST requests protected
- **Input Validation**: Multi-layer validation (Form → Service → Model)
- **Non-Root Container**: Docker container runs as unprivileged user

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key (generate: `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DJANGO_DEBUG` | No | Debug mode (`False` for production) |
| `ALLOWED_HOSTS` | No | Comma-separated allowed hosts |
| `DATABASE_URL` | No | PostgreSQL URL (SQLite if unset) |

See `.env.example` for full configuration options.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET/POST | Calculator interface |
| `/reset/` | GET | Reset calculator state |
| `/health/` | GET | Health check |
| `/admin/` | GET | Django admin interface |

## Operations Supported

- **Addition** (`add`)
- **Subtraction** (`subtract`)
- **Multiplication** (`multiply`)
- **Division** (`divide`) - with division-by-zero protection

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
black calculator/ health/ tests/
flake8 calculator/ health/ tests/
```

### Updating Dependencies

```bash
# Edit requirements.in or requirements-dev.in, then:
pip-compile requirements.in --output-file requirements.txt
pip-compile requirements-dev.in --output-file requirements-dev.txt
```

## PostgreSQL Promotion Path

To validate PostgreSQL compatibility:

```bash
# Start with PostgreSQL
docker compose -f docker-compose.yml -f docker-compose.override.yml up --build

# Run migrations
docker compose exec web python manage.py migrate

# Verify connection
docker compose exec db psql -U calc_user -d calculator_db -c "\dt"
```

## Documentation

- [Architecture Guide](docs/architecture.md) - System design and security gates
- [Setup Guide](docs/setup.md) - Detailed setup instructions

## License

MIT License - See LICENSE file for details.

## Security

For security concerns, please review the [Security Gates](docs/architecture.md#security-gates) documentation.

---

**Built with Django 5.1** | **Python 3.12+** | **PostgreSQL 16** | **Gunicorn 22**
