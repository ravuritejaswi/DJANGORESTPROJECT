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


**Implemented the Driver API with CRUD operations.
#Work Completed
- Created Driver Profile API.
- Implemented Create Driver.
- Implemented Get/List Drivers.
- Implemented Get Driver by UUID.
- Implemented Update Driver.
- Implemented Delete Driver.
- Tested Driver API using Postman.
- Implemented authentication using JWT access tokens.
#Testing
- Driver creation tested successfully.
- Driver retrieval tested successfully.
- Driver update tested successfully.
- Driver deletion tested successfully.
- Invalid Driver UUID tested and returned

Implemented Vehicle CRUD operations.
#Work Completed
- Created Vehicle API.
- Implemented Create Vehicle.
- Implemented List Vehicles.
- Implemented Retrieve Vehicle by UUID.
- Implemented Update Vehicle.
- Implemented Delete Vehicle.
- Added Driver and Vehicle Type relationships.
- Tested Vehicle APIs using Postman.
#Testing
- POST Vehicle – `201 Created`
- GET Vehicles – `200 OK`
- GET Vehicle by UUID – `200 OK`
- PATCH Vehicle – `200 OK`
- DELETE Vehicle – tested with protected relationship handling.

Implemented and tested validation for Vehicle API requests.
#Validations Implemented
- Vehicle registration number validation.
- Vehicle type validation.
- Driver ID validation.
- Required field validation.
- Duplicate vehicle registration validation.
- Driver ownership validation.
#Testing
- Valid vehicle creation – 201 Created
- Invalid Vehicle Type – 400 Bad Request
- Invalid Driver ID – 400 Bad Request
- Missing required fields – 400 Bad Request
- Duplicate registration number – 400 Bad Request
- Driver attempting to use another driver's

Implemented and tested API access permissions.
#Work Completed
- Added authenticated-user permission handling.
- Applied permissions to Vehicle List/Create API.
- Applied permissions to Vehicle Detail/Update/Delete API.
- Implemented driver ownership restriction.
- Tested authenticated and unauthorized API access.
#Testing
- Authenticated user access – successful.
- Driver managing own vehicle – successful.
- Driver attempting to manage another driver's vehicle – denied.
- Unauthenticated access – 401 Unauthorized.

Implemented nested Vehicle information inside Driver API responses.
#Work Completed
- Created VehicleNestedSerializer.
- Added Vehicle information to DriverProfileSerializer.
- Used the vehicles relationship from DriverProfile.
- Returned vehicle type and vehicle registration number in Driver API response.
#Example Response
```json
{
    "id": "...",
    "user": "...",
    "license_number": "...",
    "is_available": true,
    "rating": 5,
    "vehicles": [
        {
            "vehicle_type": "Car",
            "vehicle_number": "TS09AB1234"
        }
    ]
}

Implemented advanced querying for Vehicle API.
Filtering
Implemented filtering by:
Vehicle type.
Active/inactive status.
Driver.
Searching
Implemented search using:
Driver username.
Driver license number.
Vehicle registration number.
Vehicle model.
Pagination
Implemented page-number pagination with:
PAGE_SIZE = 2
Tested multiple pages successfully.
Ordering
Implemented ordering by:
Vehicle registration number.
Vehicle model.
Created date.
Updated date.
Testing
Search – 200 OK
Vehicle type filtering – successful.
Active/inactive filtering – successful.
Pagination – successful.
Ascending ordering – successful.
Descending ordering – successful.

Implemented centralized API error handling.
Work Completed
Used custom exception handler.
Configured custom exception handler in Django REST Framework settings.
Standardized API error responses.
Error Cases Tested
Driver Not Found
404 Not Found
Vehicle Not Found
404 Not Found
Duplicate Vehicle Registration
400 Bad Request

API Testing
Performed comprehensive API testing using Postman.
Positive Test Cases
Driver API requests.
Vehicle API requests.
Successful vehicle creation.
Successful vehicle retrieval.
Successful vehicle update.
Successful authenticated access.
Negative Test Cases
Invalid Driver UUID.
Invalid Vehicle UUID.
Duplicate vehicle registration.
Missing required fields.
Blank model.
Unauthorized requests.

Authentication Testing
Valid Bearer Token – successful.
No authentication – 401 Unauthorized.
Permission Testing
Authenticated user access – successful.
Driver ownership validation – successful.
Unauthorized user access – denied.
Validation Testing
Required fields.
Invalid Driver ID.
Invalid Vehicle Type.
Duplicate registration number.
Blank model.
Advanced API Testing
Vehicle search.
Vehicle type filtering.
Active/inactive filtering.


**Ride Booking & Ride Lifecycle APIs

Ride API Database/Model Setup
Worked on DriverProfile, VehicleType, Vehicle, RideStatus, and Ride models.
Verified model relationships, UUIDs, validations, indexes, and constraints.
Ran Django system checks and resolved setup issues.

Create Ride API
Implemented and tested POST /api/rides/.
Verified ride creation with passenger, driver, vehicle, pickup/drop locations, ride type, and fare.
Confirmed successful response with 201 Created.

Ride Request Validation
Added and tested ride request validations.
Validated pickup and drop locations.
Prevented same pickup and drop locations.
Validated ride type.
Prevented users from creating conflicting active rides.
Tested validation errors using Postman.

Ride Details API
Tested GET /api/rides/{id}/.
Configured Bearer Token authentication.
Verified passenger, driver, vehicle, status, location, fare, and timestamp details.

Ride Status Management
Implemented and tested ride status transitions.
Verified:
REQUESTED → ACCEPTED
ACCEPTED → STARTED
STARTED → COMPLETED
Tested invalid transitions and confirmed they return appropriate errors.

Driver Accept Ride
Implemented the driver accept ride API.
Tested POST /api/rides/{id}/accept/.
Verified driver assignment and REQUESTED → ACCEPTED.
Tested driver availability and ride availability validations.

Cancel Ride
Implemented and tested POST /api/rides/{id}/cancel/.
Verified successful ride cancellation.
Tested repeated/invalid cancellation and confirmed proper error handling.

Complete Ride & End-to-End Testing
Implemented and tested Start Ride and Complete Ride APIs.
Tested the complete lifecycle:
Create → Accept → Start → Complete
Tested invalid completion after a ride was already completed.
Verified expected 200, 201, and 400 responses using Postman.


1. Business Logic Layer
Implemented the business logic layer by separating ride-related operations from the API views.
Created service files under rides/services/.
Implemented ride operations such as:
Ride creation
Ride acceptance
Ride cancellation
Driver assignment
Ride status validation
Added validations to ensure:
Only registered drivers can accept rides.
Drivers must be available.
Only REQUESTED rides can be accepted.
A ride cannot be assigned to multiple drivers.
A driver cannot accept another active ride.

2. Fare Calculation
Implemented the fare calculation service in fare_service.py.
Added logic to calculate the ride fare based on the required ride details.
Used Decimal for monetary calculations to maintain accurate fare values.
Added test coverage to verify that the calculated fare is correct.

3. Transactions
Used Django's transaction.atomic to make critical ride operations atomic.
Applied transactions to the ride acceptance process.
Used select_for_update() to lock the ride record while processing acceptance.
This helps prevent two drivers from accepting the same ride at the same time.
Ensured that if an error occurs during the operation, the database changes are rolled back.

4. Testing
Tested the business logic using Django TestCase.
Verified ride creation, fare calculation, ride acceptance, cancellation, and validation scenarios.
Final result:
Found 6 test(s).
Ran 6 tests
OK


Continued working on the Ride Booking Backend project using Django REST Framework.
Worked on Task 6 – API Testing.
Created and updated test cases using Django TestCase and REST Framework APIClient.
Tested different API endpoints and verified their responses.
Worked with test users, authentication, and required test data.
Identified and fixed errors encountered while running test cases.
Verified expected HTTP status codes and API responses.
Ran the Django test suite to confirm the implemented functionality.
Debugged failed test cases and made the required code corrections. 


*****Advanced Django ORM & High-Performance Database APIs*****
#Advanced Django ORM
Worked with Django ORM and QuerySets for the ride management APIs.
Implemented efficient database querying using Django ORM.
Worked with filtering and related model relationships.

# QuerySet Operations
Implemented and tested QuerySet operations for ride data.
Worked with related fields such as user, driver, vehicle, and ride status.
Verified the API responses using Postman.

#Aggregation
Implemented database aggregation using:
Count()
Sum()
Avg()
Min()
Max()
Created aggregation API to calculate ride statistics such as total rides, completed rides, cancelled rides, average fare, and maximum fare.
Tested the aggregation API successfully with 200 OK.

#Optimize Relationships
Created and tested a deliberately slow ride API.
Measured the number of SQL queries.
Optimized relationship queries using:
select_related()
prefetch_related()
Compared SQL query performance before and after optimization.
Successfully reduced unnecessary database queries.

#Database Indexing
Identified frequently searched fields such as:
user_id
driver_id
status
created_at
vehicle_type
Added an index for vehicle_type.
Created and applied Django migrations successfully.
Verified the index using PostgreSQL EXPLAIN.
Confirmed that PostgreSQL uses the created index for the query.

#Advanced Filtering
Implemented and tested:
Date filtering
Status filtering
Driver filtering
Minimum and maximum fare filtering
Multiple filters together
Ordering
Tested the filtering API through Postman and confirmed successful 200 OK responses.

#Large Dataset Testing
Generated 5,012 ride records for large-dataset testing.
Tested API response performance with the large dataset.
Implemented and tested pagination.
Tested custom page_size values.
Verified pagination links.
Checked database query performance.
Successfully received 200 OK responses.

#Code Review & Optimization
Reviewed Django ORM code across the ride APIs.
Checked for:
Duplicate queries
Queries inside loops
Unnecessary database calls
Repeated calculations
Optimized relationship queries using select_related().
Reviewed aggregation and QuerySet implementations.
Tested the optimized APIs through Postman.
Confirmed successful 200 OK responses.

***Location-Based Driver Discovery & Geospatial Backend***
#Understand Location Data
Studied latitude, longitude, coordinates, distance, and radius.
Understood how latitude and longitude represent a driver's geographic location.
Understood how distance and radius are used for nearby-driver searches.
Learned why location data needs to be stored as numeric/geospatial values for distance calculations.

#Driver Location Model
Created the DriverLocation model.
Added fields for:
Driver
Latitude
Longitude
Last updated
Availability
Added availability status support for ONLINE, OFFLINE, and BUSY.
Created and applied Django migrations successfully.
Verified the model using Django shell.
Confirmed python manage.py check completed without issues.

#Driver Location API
Implemented the driver location update API:
POST /api/drivers/location/
Added latitude and longitude handling.
Implemented creation/update of the driver's latest location.
Tested the API successfully in Postman.
Confirmed 201 Created for the initial location creation.

#Nearby Driver API
Implemented:
GET /api/drivers/nearby/
Added latitude, longitude, and radius parameters.
Implemented nearby-driver distance calculation.
Filtered drivers based on the requested radius.
Tested the API successfully with 200 OK.

#Distance Calculation
Implemented the Haversine formula for geographic distance calculation.
Returned:
driver_id
distance_km
Sorted nearby drivers by distance.
Tested the API successfully with 200 OK.
Verified distance calculation and nearest-driver ordering.

#Driver Availability
Implemented driver availability states:
ONLINE
OFFLINE
BUSY
Updated nearby-driver filtering so that only ONLINE drivers are considered for new ride requests.
Tested all three availability states successfully:
ONLINE → driver returned
OFFLINE → driver not returned
BUSY → driver not returned

#Location Validation
Added validation for:
Invalid latitude
Invalid longitude
Missing coordinates
Invalid radius
Inactive drivers
Busy drivers
Verified invalid inputs return 400 Bad Request.
Verified inactive and busy drivers are excluded from nearby-driver results.
Successfully tested all validation scenarios in Postman.

#Performance Testing & Optimization
Created 1,000 performance-test driver records and corresponding driver locations.
Tested nearby-driver search with the large dataset.
Recorded baseline API performance of approximately 2.19 seconds.
Identified unnecessary database access while retrieving related driver IDs.
Optimized the query/code to avoid unnecessary related-object access.
Further optimized the QuerySet using .values() to retrieve only required fields.
Re-tested the API after optimization.
Improved response time to approximately 158 ms average in the subsequent tests.
Verified the optimized API continued returning 200 OK.


#WebSocket Connection & Ride Status Broadcasting
Verified the existing WebSocket configuration in consumers.py, routing.py, and asgi.py.
Connected to the ride WebSocket using Postman.
Tested ride status communication through the WebSocket.
Verified STARTED and COMPLETED ride-status events.
Verified the WebSocket receives the ride-status broadcast successfully.

#Driver Location Tracking
Verified the existing DriverLocation model and serializer.
Tested the driver location update API using PATCH.
Successfully updated driver latitude and longitude.
Verified the API returned 200 OK.
Connected to the ride WebSocket using Postman.
Updated the driver's location while the WebSocket was connected.
Successfully received the driver_location event through WebSocket.

#WebSocket Authentication & Authorization
Verified JWT authentication configuration.
Tested WebSocket connection with a valid JWT token.
Successfully connected an authenticated user.
Tested WebSocket connection without a token.
Verified that unauthenticated access was rejected with 403 Access Denied.
Tested ride-level authorization.
Verified that users without access to a ride are rejected.

#Disconnect Handling
Tested WebSocket connection and normal client disconnection.
Verified the client disconnects successfully.
Tested invalid/no-token WebSocket connections.
Verified unauthorized connections are rejected.
Updated the WebSocket disconnect handling to safely remove clients from the channel group.
Fixed the room_group_name disconnect error.
Verified valid authenticated WebSocket connections after the fix.

#Multiple Client & Real-Time Event Testing

Created separate authenticated WebSocket connections for:
Passenger
Driver
Successfully connected both clients to the same ride.
Tested ride-status updates using the Start Ride API.
Verified STARTED status was broadcast through WebSocket.
Tested Complete Ride API.
Verified COMPLETED status was broadcast through WebSocket.
Verified the ride status using GET API after the status changes.
Confirmed the complete REST API → Channel Layer → WebSocket event flow.