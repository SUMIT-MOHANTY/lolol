# Django Calculator Setup Guide

## Quick Start

### Local Development (SQLite)

1. **Clone and navigate to the project:**
   ```bash
   cd /workspace
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

   ⚠️ **Warning:** `manage.py runserver` is a single-threaded development server. It MUST NOT be used in production or demo environments exposed beyond localhost. Use Gunicorn (included in requirements.txt) for all production-equivalent deployments.

8. **Access the application:**
   - Calculator: http://localhost:8000/
   - Health Check: http://localhost:8000/health/
   - Admin: http://localhost:8000/admin/

### Production Deployment (Docker + Gunicorn)

1. **Create production environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with production values:
   # SECRET_KEY=<strong-random-key>
   # DJANGO_DEBUG=False
   # ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker compose up --build
   ```

3. **Access the application:**
   - http://localhost:8000/

### PostgreSQL Promotion Path Validation

To test the application with PostgreSQL (production-like environment):

1. **Start with PostgreSQL override:**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.override.yml up --build
   ```

2. **Verify PostgreSQL is running:**
   ```bash
   docker compose ps
   ```

3. **Run migrations against PostgreSQL:**
   ```bash
   docker compose exec web python manage.py migrate
   ```

4. **Verify database connection:**
   ```bash
   docker compose exec db psql -U calc_user -d calculator_db -c "\dt"
   ```

5. **Create superuser (optional):**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. **Stop services:**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.override.yml down
   ```

   To also remove the PostgreSQL data volume:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.override.yml down -v
   ```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Django secret key (generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DJANGO_DEBUG` | No | `False` | Debug mode (`True`/`False`) |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated list of allowed hosts |
| `DATABASE_URL` | No | - | PostgreSQL connection URL (SQLite if unset) |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Gunicorn Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GUNICORN_BIND` | `0.0.0.0:8000` | Server bind address |
| `GUNICORN_WORKERS` | `(2 * CPU) + 1` | Number of worker processes |
| `GUNICORN_TIMEOUT` | `30` | Worker timeout in seconds |
| `GUNICORN_KEEPALIVE` | `2` | Keepalive timeout in seconds |
| `GUNICORN_LOG_LEVEL` | `info` | Log level (debug, info, warning, error, critical) |

## Development Commands

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=calculator --cov-report=html

# Run specific test file
pytest tests/test_services.py
```

### Code Quality

```bash
# Format code with Black
black calculator/ health/ tests/

# Lint with Flake8
flake8 calculator/ health/ tests/
```

### Database Operations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell
```

### Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear and recollect
python manage.py collectstatic --noinput --clear
```

## Security Checklist

Before deploying to production:

- [ ] `SECRET_KEY` is set to a strong random value
- [ ] `DJANGO_DEBUG` is set to `False`
- [ ] `ALLOWED_HOSTS` includes your domain(s)
- [ ] HTTPS is configured (SSL certificate)
- [ ] Database credentials are secure (if using PostgreSQL)
- [ ] `eval()`/`exec()` scan passes: `grep -rn 'eval\|exec(' --include='*.py' .`
- [ ] Security headers are enabled (automatic when `DEBUG=False`)
- [ ] Container runs as non-root user

## Troubleshooting

### Database Connection Issues

**SQLite:**
```bash
# Check database file permissions
ls -la db.sqlite3

# Reset database (WARNING: deletes all data)
rm db.sqlite3
python manage.py migrate
```

**PostgreSQL:**
```bash
# Check PostgreSQL container logs
docker compose logs db

# Verify connection from web container
docker compose exec web python -c "from django.db import connection; connection.ensure_connection(); print('Connected!')"
```

### Static Files Not Loading

```bash
# Rebuild static files
python manage.py collectstatic --noinput --clear

# Check static files configuration
python manage.py findstatic css/calculator.css
```

### Gunicorn Issues

```bash
# Check Gunicorn logs
docker compose logs web

# Test Gunicorn configuration
python -c "import gunicorn.conf; print('Config OK')"
```

## Production Deployment Notes

### Behind a Reverse Proxy (Nginx, AWS ALB, etc.)

When running behind a reverse proxy that terminates SSL:

1. The proxy should set `X-Forwarded-Proto: https` header
2. Django's `SECURE_PROXY_SSL_HEADER` should be configured if needed
3. Gunicorn's `forwarded_allow_ips` is set to `*` by default (configurable via env)

### Scaling Considerations

- **Horizontal Scaling:** Run multiple Gunicorn containers behind a load balancer
- **Database:** Use PostgreSQL with connection pooling (PgBouncer recommended for high load)
- **Static Files:** Serve via CDN or dedicated static file server (Nginx, S3, etc.)
- **Sessions:** Configure `SESSION_ENGINE` to use cache or database for multi-instance deployments

### Health Monitoring

The `/health/` endpoint returns:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

Use this for:
- Load balancer health checks
- Container orchestration (Kubernetes liveness/readiness probes)
- Monitoring dashboards
