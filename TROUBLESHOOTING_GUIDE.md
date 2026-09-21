
# Django Backend Troubleshooting Guide

## 1. Django Container Is Not Running

Problem:
- Web container stops or restarts.

Where to check:
- Django/Gunicorn logs.

Command:
docker compose logs web --tail=100

Possible solutions:
- Check missing Python dependencies.
- Check Django settings.
- Check database connectivity.
- Check the Gunicorn startup command.

## 2. Database Connection Failure

Problem:
- Django cannot connect to PostgreSQL.

Where to check:
- Web logs and PostgreSQL logs.

Commands:
docker compose logs web --tail=100
docker compose logs postgres --tail=100

Possible solutions:
- Verify DB_HOST.
- Verify DB_PORT.
- Verify database credentials.
- Check PostgreSQL health.
- Check network configuration.

## 3. Redis Connection Failure

Problem:
- Django or Celery cannot connect to Redis.

Where to check:
- Redis and Celery logs.

Commands:
docker compose logs redis --tail=100
docker compose logs celery --tail=100

Possible solutions:
- Verify REDIS_HOST.
- Verify REDIS_PORT.
- Check Redis container status.
- Check Redis authentication settings if enabled.

## 4. Celery Worker Is Not Running

Problem:
- Background tasks are not executed.

Where to check:
- Celery logs.

Command:
docker compose logs celery --tail=100

Possible solutions:
- Check the Celery startup command.
- Check the Redis broker URL.
- Check task registration.
- Check Django settings initialization.
- Check task exceptions.

## 5. Nginx Returns 502 Bad Gateway

Problem:
- Nginx cannot reach Gunicorn.

Where to check:
- Nginx and web logs.

Commands:
docker compose logs nginx --tail=100
docker compose logs web --tail=100

Possible solutions:
- Verify the web container is running.
- Verify Gunicorn is listening on port 8000.
- Verify the Nginx upstream is configured as web:8000.
- Restart the affected service after identifying the issue.

## 6. Static Files Return 404

Problem:
- CSS, JavaScript, or other static files are unavailable.

Where to check:
- Django settings, Nginx configuration, and web container.

Commands:
docker compose exec web python manage.py collectstatic --noinput
docker compose exec nginx nginx -t

Possible solutions:
- Verify STATIC_URL.
- Verify STATIC_ROOT.
- Verify static volume sharing.
- Verify the Nginx static alias.

## 7. Migration Failure

Problem:
- Database migrations fail.

Where to check:
- Django logs and migration output.

Commands:
docker compose exec web python manage.py showmigrations
docker compose logs web --tail=100

Possible solutions:
- Review the migration error.
- Verify database connectivity.
- Check migration dependencies.
- Take an approved backup before production schema changes.

## 8. API Returns 404

Problem:
- Requested API route is not found.

Where to check:
- Django URL configuration.

Commands:
docker compose logs web --tail=100
docker compose exec web python manage.py check

Possible solutions:
- Verify the URL path.
- Check application URL inclusion.
- Check the HTTP method.
- Confirm that the endpoint exists.

## 9. API Returns 500

Problem:
- The server encounters an internal error.

Where to check:
- Django/Gunicorn logs.

Command:
docker compose logs web --tail=100

Possible solutions:
- Review the traceback.
- Check database and Redis connectivity.
- Check request data and serializer validation.
- Reproduce the issue in a safe test environment.

## 10. Container Health Check Fails

Problem:
- A service is unhealthy.

Where to check:
- Docker Compose service status and service logs.

Commands:
docker compose ps
docker compose logs SERVICE_NAME --tail=100

Possible solutions:
- Check the healthcheck command.
- Verify the service is listening on the expected port.
- Check service dependencies.
- Review the container configuration.