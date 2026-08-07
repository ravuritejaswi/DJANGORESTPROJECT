# Django REST Project

## Project Setup

Today I completed:

- Created a Django project
- Created Django apps
- Configured PostgreSQL database
- Created a Custom User Model
- Used UUID as Primary Key
- Enabled Email Login
- Ran database migrations
- Initialized Git
- Added a .gitignore file

## Technologies Used

- Python
- Django
- Django REST Framework
- PostgreSQL
- Git

## How to Run

1. Activate the virtual environment
2. Run:
   python manage.py runserver
3. Open:
   http://127.0.0.1:8000/
   









# Django REST Authentication APIs

## Features
- User Registration
- User Login
- JWT Authentication
- User Profile
- Change Password
- Logout API
- Token Blacklisting

## APIs

### Register

POST /accounts/register/

Request

```json
{
    "username": "tejaswi",
    "email": "tejaswi@gmail.com",
    "password": "Tejaswi@123"
}
```

---

### Login

POST /accounts/login/

Request

```json
{
    "email": "tejaswi@gmail.com",
    "password": "Tejaswi@123"
}
```

Response

```json
{
    "access": "<access_token>",
    "refresh": "<refresh_token>"
}
```

---

### Profile

GET /accounts/profile/

Authorization

```
Bearer <access_token>
```

---

### Change Password

POST /accounts/change-password/

```json
{
    "current_password": "Tejaswi@123",
    "new_password": "Tejaswi@456"
}
```

---

### Logout

POST /accounts/logout/

```json
{
    "refresh": "<refresh_token>"
}
```

---

## Authentication

Protected APIs require the following header:

```
Authorization: Bearer <access_token>
```





# Django REST API

## Features
- User Registration
- Login with JWT
- Logout
- Change Password
- Profile CRUD
- Swagger Documentation

## Technologies
- Django
- Django REST Framework
- Simple JWT
- DRF-YASG (Swagger)

# Work Completed

## Overview
Completed the implementation, optimization, testing, and documentation of Django REST Framework APIs.

## Features Implemented

### Logging
- Configured centralized logging.
- Generated log files for API requests and responses.
- Verified logging functionality.

### Exception Handling
- Created a custom exception handler.
- Standardized API error responses.
- Handled authentication and validation errors.

### ORM Optimization
- Optimized database queries using `select_related()`.
- Improved API performance by reducing unnecessary database hits.
- Tested optimized queries successfully.

### API Testing
Successfully tested the following APIs using Swagger:
- Register User
- Login
- Change Password
- Logout
- Create Profile
- View Profile
- Update Profile
- Delete Profile
- Restore Profile
- Profile Listing
- Search, Filter, Ordering, and Pagination

### Bug Fixes
- Fixed authentication-related issues.
- Fixed profile CRUD issues.
- Resolved query optimization errors.
- Improved custom error responses.

## Documentation
- Updated project documentation.
- Verified API endpoints and responses.
- Reviewed overall project structure.

## Result
- All implemented APIs are functioning correctly.
- Logging and exception handling are working as expected.
- ORM queries are optimized.
- Project is ready for review and GitHub submission.
