Dockerize Django Mobile Backend

Objective

Containerize the Django Mobile Backend so that the application can run
consistently across development, testing, and production environments.

Architecture:

Mobile App
    |
    v
  Nginx
    |
    v
Django / Gunicorn
    |
    +------------------> PostgreSQL
    |
    +------------------> Redis
                           |
                           v
                     Celery Worker

Task 1 --- Understand Container Architecture

Mobile App

The mobile application acts as the client and communicates with the
backend through REST APIs for authentication, ride booking, ride status,
driver information, and ride history.

Nginx

Nginx acts as a reverse proxy. It receives incoming HTTP/HTTPS requests
and forwards them to the Django application running through Gunicorn.

Django

Django contains the backend application and business logic, including
authentication, JWT authorization, user/profile management, driver
management, ride booking, validation, permissions, and REST APIs.

Gunicorn

Gunicorn is the production WSGI application server used to serve Django.

PostgreSQL

PostgreSQL is the persistent relational database used for users,
profiles, drivers, vehicles, rides, statuses, notifications, and other
application data.

Redis

Redis is used for Django caching and as the message broker for Celery.

Celery Worker

Celery processes background tasks asynchronously, including ride
notifications, completion notifications, reports, and maintenance tasks.

Component Summary

Component    Responsibility

Mobile App   Client/frontend
Nginx        Reverse proxy
Django       Backend/business logic
Gunicorn     Production application server
PostgreSQL   Persistent database
Redis        Cache and Celery broker
Celery       Background task processing

Task 2 --- Create Production Dockerfile

Purpose

Create a production Dockerfile that packages the Django backend with its
Python dependencies and starts the application using Gunicorn.

Python Base Image

FROM python:3.13-slim

The project uses Python 3.13, so the Python 3.13 slim image is used.

Working Directory

WORKDIR /app

Environment Variables

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

Sensitive values such as database passwords and Django secret keys are
not hard-coded into the Dockerfile.

Dependencies

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip     && pip install --no-cache-dir -r requirements.txt

Gunicorn was added to the project dependencies:

gunicorn==26.2.0

Application Files

COPY . .

Application files are copied into the image while files excluded by
.dockerignore are excluded from the build context.

Production Startup

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

Validation

The Django project was validated with:

python manage.py check

Result:

System check identified no issues (0 silenced).

Gunicorn 26.2.0 is installed. Direct execution of Gunicorn on Windows is
not used because Gunicorn is a Unix/Linux production server; the Docker
image provides the Linux environment where it runs.

The final Docker image build requires a working Docker Engine.

Task 3 --- Create .dockerignore

Purpose

Prevent unnecessary, development-only, and sensitive files from being
included in the Docker build context.

Required exclusions:

__pycache__/
.env
.git/
venv/
*.pyc
logs/

Additional development exclusions can include:

.venv/
env/
.env.*
.vscode/
.idea/
.pytest_cache/
.coverage
htmlcov/
*.log
db.sqlite3

The .env file is excluded so sensitive configuration such as the
Django secret key and database credentials is not copied into the Docker
image.

The .dockerignore file is located in the project root alongside
Dockerfile, manage.py, and requirements.txt.

Task 4 --- Create Docker Compose

Purpose

Docker Compose defines the services required by the backend:

web
postgres
redis
celery
nginx

Web

The web service builds the Django image and runs Gunicorn.

web -> Django/Gunicorn

PostgreSQL

The postgres service runs PostgreSQL and uses a named volume for
persistent data.

Redis

The redis service provides Redis for caching and Celery communication.

Celery

The celery service uses the Django application image and starts a
Celery worker.

Nginx

The nginx service acts as the reverse proxy and forwards requests to:

web:8000

Networking

All services are connected to the same Docker network:

backend

Containers communicate using Docker Compose service names:

nginx -> web
web -> postgres
web -> redis
celery -> redis

Inside Docker, service names are used instead of localhost.

Task 5 --- Configure PostgreSQL

Purpose

Move PostgreSQL into Docker and preserve its data using a named volume.

Database Configuration

PostgreSQL is configured through environment variables:

POSTGRES_DB: ${DB_NAME}
POSTGRES_USER: ${DB_USER}
POSTGRES_PASSWORD: ${DB_PASSWORD}

Sensitive values are supplied through environment configuration rather
than hard-coded into the Compose file.

Port

ports:
  - "5432:5432"

Persistent Volume

volumes:
  - postgres_data:/var/lib/postgresql/data

The named volume is declared with:

volumes:
  postgres_data:

This allows PostgreSQL data to remain available when the container is
stopped or recreated.

Health Check

PostgreSQL uses a pg_isready health check so dependent services can
wait for the database to become ready.

Django Connection

Inside Docker, Django connects to PostgreSQL using:

DB_HOST=postgres
DB_PORT=5432

The Docker Compose service name postgres is used instead of
127.0.0.1.

Persistence Test

After Docker Engine is available:

docker compose up -d postgres
docker compose ps

Then stop the containers:

docker compose down

Start PostgreSQL again:

docker compose up -d postgres

The named volume remains because docker compose down does not remove
named volumes by default.

Do not use docker compose down -v when testing persistence because
-v removes the named volumes.

Task 6 --- Configure Redis

Purpose

Connect Django and Celery to the Redis container.

Redis Service

Redis runs as the Compose service:

redis

and listens on:

6379

Django to Redis

Django uses Redis for caching:

Django
   |
   v
redis:6379

Celery to Redis

Celery uses Redis as its message broker:

Django
   |
   v
Redis
   |
   v
Celery Worker

Container Networking

Inside Docker, the connection must use:

redis:6379

rather than:

127.0.0.1:6379

because 127.0.0.1 inside a container refers to that same container.

Verification

After Docker Engine is available:

docker compose up -d redis
docker compose ps

The Redis health check uses:

redis-cli ping

A healthy Redis container should report a healthy status.

Task 7 --- Run Complete Application

Purpose

Start and verify the complete containerized backend.

Required services:

Django        ✓
PostgreSQL    ✓
Redis         ✓
Celery        ✓
Nginx         ✓

Start the Environment

From the project root:

docker compose up -d --build

Check Containers

docker compose ps

Expected services include:

django_web
django_postgres
django_redis
django_celery
django_nginx

Check Logs

docker compose logs web
docker compose logs postgres
docker compose logs redis
docker compose logs celery
docker compose logs nginx

API Flow

Mobile App
     |
     v
Nginx :80
     |
     v
Django/Gunicorn :8000
     |
     +----> PostgreSQL
     |
     +----> Redis
               |
               v
          Celery Worker

The APIs should be tested through Nginx.

Example:

http://localhost/api/

Use the appropriate endpoint configured by the project.

Verification Checklist

Component    Verification

Django       docker compose logs web
PostgreSQL   docker compose ps / health check
Redis        Redis health check
Celery       docker compose logs celery
Nginx        docker compose logs nginx
API          Test through Nginx

Current Dockerization Status

Task 1  Container Architecture       ✓
Task 2  Production Dockerfile        ✓ Prepared
Task 3  .dockerignore                ✓
Task 4  Docker Compose               ✓ Prepared
Task 5  PostgreSQL configuration     ✓ Prepared
Task 6  Redis configuration          ✓ Prepared
Task 7  Complete environment         Pending runtime verification

Runtime verification for Tasks 5--7 requires a working Docker Engine.

Useful Commands

Validate Compose configuration:

docker compose config

Build images:

docker compose build

Start all services:

docker compose up -d

Check services:

docker compose ps

View logs:

docker compose logs

Stop containers without deleting named volumes:

docker compose down

Avoid:

docker compose down -v

when PostgreSQL persistence needs to be preserved.