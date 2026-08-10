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





## EPIC 02 — Django Mobile Backend: Core Business API's

# Database Modeling & Business Module Architecture
I choose Ride Booking mobile application
# Design the DataBase 
1. Create an ER diagram containing:
                         ┌────────────────────┐
                         │       User         │
                         │  Django Auth User  │
                         └─────────┬──────────┘
                                   │
                         OneToOne  │
                                   ▼
                         ┌────────────────────┐
                         │   DriverProfile    │
                         │--------------------│
                         │ user               │
                         │ license_number     │
                         │ is_available       │
                         │ rating             │
                         └─────────┬──────────┘
                                   │
                              ForeignKey
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      Vehicle       │
                         │--------------------│
                         │ driver             │
                         │ vehicle_type       │
                         │ vehicle_number     │
                         │ model              │
                         │ color              │
                         │ is_active          │
                         └─────────┬──────────┘
                                   │
                                   │
                    ┌──────────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │    VehicleType      │
          │---------------------│
          │ name                │
          │ description         │
          │ is_active           │
          └─────────────────────┘


User ────────────────┐
                     │
DriverProfile ───────┤
                     │
Vehicle ─────────────┤
                     │
RideStatus ──────────┤
                     ▼
              ┌───────────────┐
              │     Ride      │
              │---------------│
              │ user          │
              │ driver        │
              │ vehicle       │
              │ status        │
              │ ride_type     │
              │ pickup        │
              │ drop          │
              │ fare          │
              │ scheduled_at  │
              └───────────────┘

              RideStatus
              ┌────────────────┐
              │ name           │
              │ description    │
              └────────────────┘

#Models
*DriverProfile
Represents the driver's profile associated with a Django user.
Main fields:
user — One-to-One relationship with User
license_number — Driver's license number
is_available — Indicates whether the driver is currently available
rating — Driver rating
created_at — Profile creation timestamp
updated_at — Last update timestamp

*VehicleType
Represents the type/category of a vehicle.
Main fields:
name - Vehicle type name
description - Description of the vehicle type
is_active - Indicates whether the vehicle type is active
created at
updated_at

*Vehicle
Represents a vehicle registered for a driver.
Main fields:
driver - DriverProfile relationship
vehicle_type - VehicleType relationship
vehicle_number - Vehicle registration number
model - Vehicle model
color - Vehicle color
is active - Indicates whether the
vehicle is active
created_at
updated_at

*RideStatus
Represents the current status of a ride.
Examples:
Requested
Accepted
Started
Completed
Cancelled
Main fields:
name
description
created_at
updated_at

*Ride
Represents a ride requested by a user.
Main fields:
user - User who requested the ride
driver - Assigned driver
vehicle - Vehicle used for the ride
status - Current ride status
ride_type - NOW or SCHEDULED
pickup_address
drop_address
pickup_latitude
pickup_longitude
drop_latitude
drop_longitude
fare
scheduled at
created at
updated_at

3.Document Relationships
Relationships:
User → DriverProfile: One-to-One
DriverProfile → Vehicle: One-to-Many
VehicleType → Vehicle: One-to-Many
User → Ride: One-to-Many
DriverProfile → Ride: One-to-Many
Vehicle → Ride: One-to-Many
RideStatus → Ride: One-to-Many
↓
4.Business Rules
A driver profile belongs to a user.
A driver can have multiple vehicles.
A vehicle belongs to a vehicle type.
A user can request multiple rides.
A ride can be assigned to a driver and vehicle.
Every ride has a status.
Ride type can be NOW or SCHEDULED.
Ride fare cannot be negative.
Active/inactive flags control driver and vehicle availability.

5.Database Constraints
Ride status names are unique.
Ride fare cannot be negative.
Required fields cannot contain NULL.
Foreign keys maintain valid relationships.
Indexes are created for frequently queried ride fields.
Ride indexes are created for user, driver, status, and created_at.

6.Django Admin
The following business models are registered in Django Admin:
- DriverProfile
- VehicleType
- Vehicle
- RideStatus
- Ride
Ride Admin provides:
- List display
- Search
- Filters
- Ordering

7. Migration Testing
Migrations were created and applied successfully.
Commands used:
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations rides
Migration rollback was tested using:
python manage.py migrate rides 0001
The migration was restored using:
python manage.py migrate rides
Final migration status was verified successfully.