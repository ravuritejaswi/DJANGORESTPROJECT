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

#Notification Module
Implemented the basic notification functionality in the Django REST project.
Created the notification model.
Added fields required to store notification information.
Connected notifications with users.
Added notification-related functionality to the accounts application.
Created and applied the required database migration.

#Notification Data Handling
Implemented the required handling of notification data.
Added notification fields such as:
Title
Message
Notification type
Read/unread status
Creation timestamp
Configured the notification model properly.
Added string representation for notifications.

#Background Task Processing
Implemented background processing using Celery.
Configured Celery in the Django project.
Created asynchronous Celery tasks.
Used .delay() to send tasks to the background worker.
Verified that tasks are picked up and executed by the Celery worker.

#Redis Integration
Configured Redis as the message broker for Celery.
Connected Celery with Redis.
Started Redis successfully.
Started the Celery worker.
Verified the connection between Django, Celery and Redis.
The worker successfully showed a Redis connection such as:
Connected to redis://127.0.0.1:6379

#Celery Job Execution and Retry
Implemented and tested background jobs with retry functionality.
Created Celery tasks for notification-related operations.
Tested successful task execution.
Implemented retry behavior for failed jobs.
Verified that a task can retry and eventually complete successfully.
Example result verified:
success: True
attempt: 3
message: Job completed successfully

#Notification Tasks
Implemented notification-related background tasks.
The project contains tasks such as:
send_ride_notification
send_driver_assignment_notification
send_reminder_notification
send_ride_completion_notification
These tasks allow notification operations to be processed asynchronously by Celery instead of blocking the main application.

#Prevent Duplicate Notifications
Implemented duplicate notification prevention.
Implementation
Added an event_id to the Notification model and created a unique constraint using:
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["user", "event_id"],
            name="unique_user_event_notification"
        )
    ]
This ensures that the same user cannot receive multiple notifications for the same event.
#Testing
A notification was created with:
event_id = test-event-001
When another notification with the same user and event ID was attempted, Django/PostgreSQL correctly rejected it with:
IntegrityError:
duplicate key value violates unique constraint
"unique_user_event_notification"
This confirms that duplicate notifications are successfully prevented.

#Testing
Performed testing of the notification and background-job functionality.
The following scenarios were tested:
8.1 Successful Job
Verified that a Celery task executes successfully and returns the expected result.
Status: ✅ Passed
8.2 Failed Job
Created a test task that intentionally raises an exception:
@shared_task
def failed_test():
    raise Exception("Test Failure")
The Celery worker correctly captured the failure:
Exception: Test Failure
Retry
Verified that failed tasks are retried and eventually succeed.
Example:
attempt: 3
success: True
Job completed successfully on attempt 3
Status: ✅ Passed
8.4 Duplicate Prevention
Verified that creating the same notification for the same user and event is rejected by the database unique constraint.
Notification Retrieval
Verified that notifications can be retrieved for the user.
Status: ✅ Passed
8.6 Mark as Read
Verified the notification read/unread functionality.

***Caching, API Performance & Advanced Backend Testing — Tasks 1–7 Documentation***
#Understand Caching
Objective:

Understand how caching improves API performance by avoiding repeated database queries for frequently requested data.

Work Done
Studied the flow:
Client
   ↓
API
   ↓
Cache
   ↓
Database
Understood that PostgreSQL/database queries can be expensive when the same information is requested repeatedly.
Learned that a cache stores frequently accessed data temporarily so subsequent requests can be served faster.
Understood the concepts of:
Cache Hit — requested data is available in the cache.
Cache Miss — requested data is not available, so the application retrieves it from the database.
Cache Expiration — cached data is automatically removed after a specified period.
Outcome:
Understood the purpose of caching and how it can reduce database load and improve API response time.



#Configure Redis Cache
Objective

Configure Redis as the caching backend for suitable APIs.

Work Done
Configured Redis in Django settings.
Added Django cache configuration using Redis.
Redis was configured as:
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    },
}
Identified APIs/data suitable for caching, including:
Nearby drivers
Vehicle types
Ride configuration
Frequently accessed profile information
Outcome:
Redis caching infrastructure was configured and made available for API-level caching.




#Cache Nearby Drivers
Objective

Implement caching for frequently requested driver-location information.

Work Done
Reviewed the nearby-driver API and driver location data.
Designed a cache strategy for frequently requested location information.
Used driver location as a suitable candidate because nearby-driver requests can occur frequently.
Implemented/considered cache lookup before querying the database.
Understood the expected flow:
Nearby Driver Request
        ↓
Check Redis Cache
        ↓
   ┌────┴────┐
   ↓         ↓
Cache Hit  Cache Miss
   ↓         ↓
Return     Query DB
Data          ↓
           Store in Cache
                ↓
           Return Data
Outcome:
Established a caching approach for nearby-driver information to reduce repeated database queries.



#Cache Invalidation
Objective

Prevent stale driver location and availability information from being returned from the cache.

Work Done
Reviewed the relationship between driver updates and cached data.
Identified driver location and availability as data that can become stale.
Implemented/designed cache invalidation when driver information changes.
Followed the flow:
Driver Location/Availability Update
                ↓
        Invalidate Old Cache
                ↓
        Store Updated Data
                ↓
        Serve Fresh Data
Considered cache expiration as an additional protection against stale information.
Outcome:
Established a cache invalidation strategy so that updated driver information is not incorrectly served from an old cache entry.




API Performance Benchmark
Objective

Compare API performance with and without caching.

Work Done
Reviewed API performance measurement requirements.
Compared the expected behavior of:
API without cache
API with cache
Focused on measuring:
Metric	         Without Cache	      With Cache
Response time	   Measured	           Measured
Database queries	Higher	           Reduced
Cache hits	          0	               Increased
Cache misses	     N/A	           Recorded

Used cache-hit and cache-miss behavior to understand the performance difference.
Evaluated database query reduction as an important indicator of caching effectiveness.
Outcome:
Established a performance benchmarking approach for evaluating the benefit of Redis caching.
Note: If you have actual benchmark numbers from your project, they should be added here instead of using estimated values.



#Complete Backend Test Suite
Objective
Create comprehensive automated tests covering the backend functionality.
Work Done
Created and executed tests covering:
Authentication
Profiles
Drivers
Vehicles
Rides
Fare
Location
Notifications
WebSockets
Permissions

Both types of tests were included:
Positive Tests

Tested valid scenarios such as:
Authenticated API requests
Successful Driver and Vehicle operations
Valid ride creation
Successful fare calculation
Valid driver location updates
Valid WebSocket connections
Successful notifications
Negative Tests

Tested invalid or unauthorized scenarios such as:
Unauthenticated requests
Invalid data
Invalid JWT tokens
Unauthorized resource access
Invalid WebSocket connections
Invalid ride payloads
Permission violations
Verification

The complete backend test suite was executed successfully:
Found 54 test(s).
Ran 54 tests in 114.338s
OK

Outcome:
All 54 backend tests passed successfully, confirming that the implemented functionality and security checks were working as expected.


#Security Testing
Objective
Perform security testing by attempting unauthorized or invalid operations and fixing discovered issues.
Security Tests Performed

1. Unauthorized API Access
Verified that unauthenticated users cannot access protected APIs.
Unauthenticated Request
        ↓
Authentication Check
        ↓
401 Unauthorized

2. Invalid JWT
Tested requests using an invalid JWT token.
Expected behavior:

Invalid JWT
    ↓
Authentication Failure
    ↓
401 Unauthorized

3. User Accessing Another User's Ride
Created rides belonging to different users and verified that one user cannot access another user's ride.
Expected result:

User 2 → User 1's Ride
             ↓
        Access Denied

4. Driver Accessing Another Driver's Data
Tested driver ownership restrictions.
A driver attempting to access another driver's profile was rejected.

5. Invalid WebSocket Connection
Tested:
Missing token
Invalid token
Unauthorized user
The WebSocket consumer correctly rejects invalid connections.

6. Invalid Request Payloads
Tested invalid ride data such as:
Empty pickup address
Empty drop address
Invalid coordinates
Invalid ride type
Negative fare
The API correctly returned validation errors.

7. Excessive API Requests
Tested repeated API requests to verify throttling behavior.
The test checked for:
HTTP 429 — Too Many Requests
Security Fixes
During testing, security issues were identified and addressed, including:
Authentication protection for protected APIs.
Ride ownership protection.
Driver ownership protection.
WebSocket authentication.
Invalid JWT rejection.
Request validation.
API throttling.
Final Verification
Found 54 test(s).
Ran 54 tests in 114.338s
OK

Outcome:
Security testing was completed successfully, and the complete test suite passed with 0 failures.


***Advanced Django ORM & Database Optimization***

#Study Advanced QuerySets
Studied and practiced advanced Django ORM QuerySet operations:
filter() — retrieve records matching specific conditions.
exclude() — exclude records matching a condition.
Q() — build complex queries using AND, OR, and NOT conditions.
F() — compare or update database fields directly.
annotate() — add calculated values to each QuerySet object.
aggregate() — perform calculations such as Sum, Avg, Max, Min, and Count.
values() — retrieve selected fields as dictionaries.
values_list() — retrieve selected fields as tuples or flat lists.
exists() — efficiently check whether matching records exist.
distinct() — remove duplicate query results.
Created/practiced examples for the required QuerySet operations and applied them to the ride-management backend.

#Create Ride History APIs
Implemented and verified ride-history related APIs:
GET /api/rides/history/
GET /api/rides/active/
GET /api/rides/completed/
GET /api/rides/cancelled/
The APIs retrieve rides based on the authenticated user and support ride-related filtering requirements.
Additional ride APIs implemented/verified during the work included:
GET /api/rides/driver-history/
GET /api/rides/daily-count/
GET /api/rides/aggregations/
Used Django QuerySets to filter rides based on user, status, driver, date, and other ride information.

#Implement Aggregation
Implemented the Ride Aggregations API:
GET /api/rides/aggregations/
The API returns:
Total rides
Completed rides
Cancelled rides
Total earnings
Average fare
Maximum fare
Minimum fare
Used Django aggregation functions:
Count()
Sum()
Avg()
Max()
Min()
Conditional Q() expressions were used for completed and cancelled ride counts.
The aggregation implementation was later refactored to calculate the required values efficiently through a single database aggregation query.

#Find and Optimize N+1 Queries
Created/tested a ride query scenario to identify unnecessary database queries when accessing related objects.
The N+1 problem was addressed using:
select_related()
Related objects such as:
User
Driver
Vehicle
Ride Status
are fetched efficiently with the main Ride query.
The o
This reduced unnecessary database access when processing related ride information.

#Database Indexing
Identified frequently searched and filtered Ride fields.
Implemented useful composite indexes:
models.Index(
    fields=["user", "-created_at"],
    name="ride_user_created_idx",
)

models.Index(
    fields=["driver", "-created_at"],
    name="ride_driver_created_idx",
)

models.Index(
    fields=["status", "-created_at"],
    name="ride_status_created_idx",
)

The Ride UUID primary key is already indexed because it is the primary key, so an unnecessary additional index was not created for it.
Created and applied the database migration successfully.
Performance comparison
Using PostgreSQL EXPLAIN ANALYZE:
Measurement	Before Indexing	After Indexing
Query plan	             Sequential Scan	      Index Scan
Execution time	            1.477 ms	            0.160 ms
Index used	                 ❌ No	               ✅ Yes

The tested query improved from 1.477 ms to 0.160 ms, demonstrating the benefit of indexing for the tested dataset/query.

#Large Dataset
Prepared the backend for large-dataset testing by generating several thousand Ride records.
Tested the backend against a larger number of records for:
Pagination
Filtering
Searching
Sorting
Aggregation
The existing Django REST Framework pagination configuration was used to handle large result sets without returning all records at once.
The aggregation API was also tested against the larger dataset.

#Refactoring
Reviewed the queries implemented during the day's work and removed unnecessary database calls.
Refactoring performed
Removed unnecessary separate count() queries when the result data was already being retrieved.
Avoided duplicate database queries.
Refactored ride aggregation calculations into a single aggregate() query.
Retained select_related() optimizations to prevent N+1 queries.
Kept bulk_create() for efficient large-dataset generation.
Reviewed loops to ensure database queries were not unnecessarily executed inside them.
Aggregation optimization
Instead of performing separate queries for:
Total rides
Completed rides
Cancelled rides
Fare calculations
the values were combined into one aggregation operation using:
Count()
Sum()
Avg()
Max()
Min()
Q()
This reduced unnecessary database communication.
Verification
After refactoring:
Ran 63 tests in 151.277s
OK
All existing tests continued to pass.

#Testing & Git
Performed final testing of the backend APIs through Postman, including:
Authentication
Ride APIs
Ride history
Active rides
Completed rides
Cancelled rides
Driver APIs
Vehicle APIs
Location APIs
Aggregation
Pagination
Filtering
Searching
Sorting
Negative/unauthorized requests
WebSocket authentication
Security-related scenarios such as missing/invalid JWTs and invalid requests were also verified.
The complete Django test suite was successfully executed:
Ran 63 tests
OK
Reviewed the modified backend files and prepared the work for meaningful Git commits and repository push.


#####Django Backend Architecture & Service Layer Refactoring
# Django Backend Architecture Review

## Objective

Reviewed the existing Django backend to identify architectural issues before introducing a cleaner service-layer architecture.

## Components Reviewed

- Permissions
- Celery Tasks
- WebSocket Consumers
- Models
- Serializers
- Views
- URLs
- Services
- Utilities

---

## 1. Permissions

### Observations

- Permission classes are used for API authorization.
- Permission logic should remain focused on access control.
- Business logic should not be duplicated inside permission classes.

### Problem Identified

Some authorization-related logic can be centralized and reused more consistently.

---

## 2. Celery Tasks

### Observations

- Celery is used for background notification processing.
- Notification database creation is currently performed directly inside Celery tasks.

### Problem Identified

Business logic inside tasks can become difficult to reuse.

### Improvement

Move reusable notification business operations into the service layer and keep Celery tasks focused on background execution.

---

## 3. WebSocket Consumers

### Observations

- RideConsumer handles WebSocket connection management.
- JWT authentication and ride-access checks are performed by the consumer.
- Database access is performed during ride-access validation.

### Problem Identified

The consumer contains both communication handling and business/access logic.

### Improvement

Move reusable ride-access/business operations into services while keeping the consumer focused on WebSocket communication.

---

## 4. Models

### Observations

- Models define database structure and relationships.
- Ride contains database constraints and indexes.
- Foreign-key relationships are defined appropriately.

### Problem Identified

Business workflows should be reviewed to ensure they are not tightly coupled to model implementation.

### Improvement

Keep models focused primarily on data representation, relationships, constraints, and model-level behavior.

---

## 5. Serializers

### Observations

- Serializers handle API serialization and validation.

### Problem Identified

Complex business workflows inside serializer create/update methods can make serializers difficult to maintain.

### Improvement

Keep validation in serializers and move complex business operations into services.

---

## 6. Views

### Observations

- Views handle API requests and responses.
- Some views also contain database operations and business decisions.

### Problems Identified

- Views can become large.
- Business logic can become tightly coupled to API endpoints.
- Reusable business operations may be duplicated.
- Testing business logic through API views becomes more difficult.

### Improvement

Keep views thin and move reusable business logic into services.

---

## 7. URLs

### Observations

- URLs map API endpoints to views and viewsets.
- URL configuration is separated from business logic.

### Problem Identified

No major architectural issue identified in URL routing.

### Improvement

Maintain URL configuration as a routing layer only.

---

## 8. Services

### Observations

- A services package already exists.
- Business logic is not yet consistently centralized in the service layer.

### Problem Identified

Some business logic remains in views, Celery tasks, and WebSocket consumers.

### Improvement

Use services as the central layer for reusable business operations.

---

## 9. Utilities

### Observations

- Utility/helper functionality should remain reusable and independent of API views.

### Problems Identified

- Repeated helper logic can lead to duplication.
- Generic utilities and business-specific logic should remain separated.

### Improvement

Centralize generic reusable helper functions in utility modules.

---

# Overall Architectural Problems Identified
1. Business logic is distributed across views, Celery tasks, and WebSocket consumers.
2. Views can contain both HTTP handling and business logic.
3. Some database operations are directly coupled to communication layers.
4. Service-layer usage is not yet consistent.
5. Reusable business operations should be centralized.
6. Authorization, validation, and business logic should have clearly separated responsibilities.
# Proposed Architecture

Request:

    URL
      ↓
    View
      ↓
    Serializer / Validation
      ↓
    Service Layer
      ↓
    Model / Database

Background processing:

    Celery Task
      ↓
    Service Layer
      ↓
    Database

Real-time processing:

    WebSocket Consumer
      ↓
    Service Layer
      ↓
    Database

# Conclusion
The existing backend is functional and has working authentication, REST APIs, Celery tasks, WebSockets, database optimization, and tests. The main architectural improvement required is to separate reusable business logic from API views and other communication layers by consistently introducing and using a service layer.


# Django Backend Layer Responsibilities
## Objective
Identify the responsibility of each architectural layer and define how requests should flow through the backend.
## Architecture

Request
   ↓
Serializer
   ↓
View
   ↓
Service
   ↓
Django ORM
   ↓
Database

## 1. Request / URL Layer
Responsibilities:
- Route incoming requests.
- Map URLs to views.
- Pass URL parameters and query parameters.
Should not contain business logic or database operations.

## 2. Serializer Layer
Responsibilities:
- Validate incoming request data.
- Serialize model data.
- Deserialize request data.
- Handle field-level and object-level validation.
Should not contain complex business workflows.

## 3. View Layer
Responsibilities:
- Handle HTTP requests and responses.
- Apply authentication and permissions.
- Invoke serializers.
- Call service-layer operations.
- Return appropriate HTTP responses.
Views should remain thin and should not contain complex business logic.

## 4. Service Layer
Responsibilities:
- Contain reusable business logic.
- Handle ride-related business operations.
- Coordinate multiple database operations.
- Provide reusable operations for REST APIs, Celery tasks, and WebSocket consumers.
Examples:
- Ride creation
- Ride cancellation
- Driver assignment
- Ride completion
- Fare/business calculations
- Notification workflows

## 5. Repository / ORM Layer
The project currently uses Django ORM for database access.
Responsibilities:
- Query database records.
- Create, update, and delete records.
- Perform filtering and aggregation.
- Handle relationships.
- Apply query optimizations such as select_related and prefetch_related.

A separate repository abstraction is not currently required unless introduced by the project architecture.

## 6. Database Layer
The project uses PostgreSQL.
Responsibilities:
- Persist application data.
- Maintain relationships.
- Enforce database constraints.
- Maintain indexes.
- Execute database queries.
- Maintain data integrity.

## Existing Backend Mapping
| Component | Responsibility |
|---|---|
| urls.py | URL routing |
| serializers.py | Serialization and validation |
| views.py | HTTP/API handling |
| permissions.py | Authorization |
| services/ | Business logic |
| Celery tasks | Background execution |
| consumers.py | WebSocket communication |
| models.py | Data models and database structure |
| Django ORM | Database access |
| PostgreSQL | Data persistence |

## Target Responsibility Separation
REST API:

Request
  ↓
URL
  ↓
View
  ↓
Serializer
  ↓
Service
  ↓
Django ORM
  ↓
PostgreSQL

Background task:

Celery
  ↓
Service
  ↓
Django ORM
  ↓
PostgreSQL

WebSocket:

WebSocket Consumer
  ↓
Service
  ↓
Django ORM
  ↓
PostgreSQL

## Main Architectural Principle
Each layer should have a clear responsibility.
Views should handle HTTP concerns.
Serializers should handle validation and serialization.
Services should handle business logic.
Django ORM should handle database access.
Models should represent application data and database constraints.
Celery tasks should handle background execution.
WebSocket consumers should handle real-time communication.
Permissions should handle authorization.


###Identify Responsibilities
Objective:
Understand and separate the responsibilities of each layer in the backend API architecture.

API flow
Request
   ↓
Serializer
   ↓
View
   ↓
Service
   ↓
Repository / ORM
   ↓
Database
Work completed

Reviewed the responsibilities of the major backend layers:
Request — receives HTTP request data from the client.
Serializer — validates and transforms request/response data.
View — handles HTTP requests, permissions, calls services, and returns responses.
Service — contains business logic and application operations.
Repository/ORM — performs database queries using Django ORM.
Database — stores persistent application data.
The separation helps prevent views from becoming too large and keeps business logic reusable and maintainable.

Result
The backend architecture was reviewed with a clear separation between API handling, business logic, and database operations.

###Refactor Large Views

Objective:
Identify views containing excessive business logic and move that logic into service functions.
Areas identified
The following types of logic were reviewed:
Database operations
Business calculations
Validation
Conditional business rules
Notification processing
Driver location processing
Nearby-driver calculations
Refactoring completed
Ride operations were moved into ride_service.py, including:
create_ride()
accept_ride()
cancel_ride()
start_ride()
complete_ride()

Driver-related processing was moved into driver_service.py, including:
update_driver_location()
find_nearby_drivers()
calculate_distance()
Fare processing was separated into fare_service.py.
Notification processing was separated into notification_service.py.

Result
The API views became thinner and mainly handle:

Request
   ↓
Validation / permissions
   ↓
Service call
   ↓
Response

This improved maintainability and separation of concerns.

###Create Service Modules

Objective:
Organize business logic into focused service modules.

Service structure
rides/
└── services/
    ├── user_service.py
    ├── driver_service.py
    ├── ride_service.py
    ├── fare_service.py
    └── notification_service.py
Responsibilities
Service	Responsibility
user_service.py	User-related business operations
driver_service.py	Driver availability, location and nearby-driver operations
ride_service.py	Ride creation and ride lifecycle operations
fare_service.py	Fare calculation
notification_service.py	Notification-related business operations
Result

Business logic was separated from API views into focused service modules.

The service layer provides a cleaner architecture and makes business operations easier to reuse and test.

###Create Reusable Utilities

Objective:
Identify repeated functionality and move it into reusable utility modules.
Utility structure
rides/
└── utils/
    ├── validators.py
    ├── exceptions.py
    ├── helpers.py
    └── constants.py
Work completed
validators.py
Common coordinate validation was centralized.
Latitude validation
Longitude validation
Required coordinate validation
Numeric validation
helpers.py
Common driver information processing was centralized, including retrieving a driver's display name.
constants.py
Frequently used ride-status values were organized as constants:
REQUESTED
ACCEPTED
DRIVER_ARRIVING
STARTED
COMPLETED
CANCELLED
exceptions.py
A reusable service-level exception structure was introduced.

Result
Repeated functionality was centralized, reducing duplicate code and making future maintenance easier.

###Standardize API Responses

Objective:
Provide a consistent response format across APIs.
The existing response utility was used:
core/responses.py
Success response
The standardized structure is:

{
    "success": true,
    "message": "Ride created successfully",
    "error_code": null,
    "data": {}
}
Error response
The standardized error structure is:
{
    "success": false,
    "message": "Ride cannot be cancelled",
    "error_code": "INVALID_RIDE_STATUS",
    "data": null
}
Work completed
The response helpers:

success_response()
error_response()
were used for major ride-related API responses.
Affected operations included:

Ride acceptance
Ride cancellation
Ride start
Ride completion
Fare calculation
Driver location update
Ride status update
Existing tests were also updated where necessary to validate the new response structure.
Result

API responses now follow a consistent success/error contract.

###Refactor URLs & Applications

Objective:
Review application boundaries, organize URLs, and introduce API versioning.
Application responsibilities
The backend responsibilities were organized around:

accounts
    ↓
Authentication / account functionality

rides
    ↓
Rides / drivers / vehicles / location / fare

core
    ↓
Shared response utilities
API versioning

The existing API routes were preserved for backward compatibility.
A versioned API structure was added:
/api/v1/
This provides routes such as:
/api/v1/rides/
/api/v1/rides/history/
/api/v1/rides/active/
/api/v1/rides/completed/

/api/v1/drivers/
/api/v1/drivers/nearby/

/api/v1/vehicles/

/api/v1/accounts/

/api/v1/notifications/

The original /api/ routes were retained so existing clients and tests would not be unnecessarily broken.

Result

The project now has a clearer URL structure and an API-versioning approach that can support future versions such as:

/api/v2/

without immediately removing the existing API.

###Code Review & Git

Objective:
Perform final code-quality checks after the refactoring.

Formatter
Black was installed and used to format the relevant project files.
Black
Version: 26.5.1
Import cleanup
isort was installed and used to organize imports in the files involved in the refactoring.
isort
Version: 9.0.1
Unused imports identified during linting were reviewed and removed where appropriate.

Linter
Flake8 was installed and used to identify:
Unused imports
Incorrect spacing
Long lines
Missing blank lines
Trailing whitespace
Missing newline characters
Import placement issues
The identified issues were reviewed as part of the code-quality cleanup.
Django validation
The project was checked using:
python manage.py check
Result:

System check identified no issues (0 silenced).
Testing

The complete test suite was executed after the refactoring.
Final result:
Ran 74 tests
OK
This confirmed that the refactoring and code-quality changes did not break the existing tested functionality.


****Advanced API Security & OWASP-Based Security Testing****
1. Introduction
Objective
The objective of this security audit was to identify and test common API security vulnerabilities in the Django REST Framework backend.

The following areas were reviewed:
Authentication and authorization
IDOR / Broken Access Control
Permission enforcement
Input validation
Rate limiting
Django security configuration
JWT security
Sensitive configuration protection

2. Security Findings
Finding 1 — IDOR / Broken Object-Level Authorization
Issue
Tested whether one authenticated user could access another user's ride by changing the ride ID.
Severity
High
Affected API
GET /api/rides/{ride_id}/
Test
A user attempted to access a ride belonging to another user by changing the UUID in the URL.
Example:
User A → /api/rides/<User-A-ride-ID>/
Then:
User A → /api/rides/<User-B-ride-ID>/
Risk
If object-level authorization were missing, a user could access another user's ride information by guessing or obtaining the ride ID.
This could expose sensitive ride information.
Fix
The API uses object-level permission enforcement through the ride permission configuration:
permission_classes = [
    IsAuthenticated,
    IsRideOwnerOrDriver,
]
Testing Result
PASS
Unauthorized access was rejected with:
403 Forbidden

3. Permission Testing
Finding 2 — API Permission Enforcement
Issue
Verified access permissions for different user roles.
Severity
High
Affected APIs
/api/rides/
/api/drivers/
/api/vehicles/
Roles Tested
Admin
Driver
Passenger/User
Unauthenticated User
Risk
Incorrect permissions could allow users to create, update, delete, or view resources they should not access.
Fix
DRF authentication and custom permission classes are used.
Examples:
IsAuthenticated
IsRideOwnerOrDriver
IsOwnDriverProfile
IsAdminRole
Testing Result
Permission behavior was tested using authenticated users and unauthorized requests.
Unauthorized operations returned:
403 Forbidden
while permitted operations returned successful responses such as:
200 OK
201 Created
Result: PASS

4. Input Validation
Finding 3 — Malicious and Unexpected Input
Issue
Tested APIs with invalid and unexpected input.
Severity
Medium
Affected API
POST /api/rides/
GET /api/rides/{ride_id}/
Inputs Tested
Empty strings
Invalid IDs
Invalid numbers
Invalid coordinates
Unexpected values
Invalid JSON fields
Invalid resource IDs
Examples Tested
Empty pickup address:

{
    "pickup_address": ""
}

Result:
400 Bad Request
Invalid UUID:
GET /api/rides/abc/
Result:
404 Not Found
Risk
Insufficient input validation could result in invalid database records, application errors, or unexpected application behavior.
Fix
Input validation is handled through Django REST Framework serializers and model validation.
Testing Result
Invalid input was rejected safely.
Examples:
400 Bad Request
404 Not Found
Valid ride creation returned:
201 Created
Result: PASS

5. Rate Limiting
Finding 4 — API Rate Limiting
Issue
Tested whether sensitive endpoints reject excessive requests.
Severity
High
Affected APIs
Sensitive APIs include:
Login
Registration
Password Reset
OTP
Ride Creation
Configuration
The project uses DRF throttling:

"DEFAULT_THROTTLE_CLASSES": [
    "rest_framework.throttling.AnonRateThrottle",
    "rest_framework.throttling.UserRateThrottle",
]

Sensitive endpoint rates were configured, including:
login          → 5/minute
registration   → 5/minute
password_reset → 5/minute
otp            → 5/minute
ride_creation  → 10/minute
Risk
Without rate limiting, attackers could perform:
Brute-force login attempts
OTP abuse
Password-reset abuse
Excessive ride creation requests
Testing Result
Repeated login requests produced:
429 Too Many Requests
with a response indicating that the request had been throttled.
Result: PASS

6. Django Security Configuration
Finding 5 — Secure Django Configuration
Issue
Reviewed Django security-related configuration.
Severity
High
Areas Reviewed
DEBUG
SECRET_KEY
ALLOWED_HOSTS
CSRF
Secure cookies
Session settings
Security headers
HTTPS configuration
Environment variables
Fix
Sensitive configuration is loaded from .env.
Example:
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
Production-oriented security settings were also configured.
The .env file was added to .gitignore and removed from Git tracking.
Testing Result
Django system check passed:
System check identified no issues (0 silenced).
The existing test suite also passed:
Ran 74 tests
OK
Result: PASS

7. JWT Security
Finding 6 — JWT Authentication Security
Issue
Reviewed JWT authentication and token lifecycle behavior.
Severity
High
Affected APIs
Authenticated APIs such as:
/api/rides/
/api/drivers/
/api/vehicles/
Security Checks
The following were tested:
Access-token expiration
Refresh-token behavior
Invalid-token rejection
Expired-token rejection
Token blacklisting
Configuration
The project uses:
"rest_framework_simplejwt.authentication.JWTAuthentication"
Access-token lifetime:
30 minutes
Refresh-token lifetime:
1 day
The JWT blacklist application is enabled:
"rest_framework_simplejwt.token_blacklist"
Risk
Weak JWT handling could allow unauthorized users to access protected resources using forged, expired, or invalid tokens.
Testing Result
Invalid and expired tokens were rejected.
Refresh-token behavior and token invalidation were verified.
Result: PASS

8. Authentication and Authorization
Finding 7 — Authentication Enforcement
Issue
Verified that protected APIs require authentication.
Severity
High
Affected APIs
Protected endpoints throughout the backend, including:
/api/rides/
/api/drivers/
/api/vehicles/
Risk
If authentication were missing, unauthenticated users could access protected resources.
Fix
DRF JWT authentication is configured globally:
"DEFAULT_AUTHENTICATION_CLASSES": (
    "rest_framework_simplejwt.authentication.JWTAuthentication",
),

Individual APIs also use:
permission_classes = [IsAuthenticated]
where appropriate.
Testing Result
Unauthenticated access to protected resources was rejected.
Result: PASS


*******Automated Testing & Backend Quality Engineering

#Understand Django Testing

Studied the fundamentals of Django testing and understood the purpose of different testing approaches.
Topics covered
Unit Testing — Testing individual functions, methods, or components independently.
Integration Testing — Testing how multiple backend components work together.
API Testing — Testing REST API endpoints, request data, authentication, status codes, and responses.
Test Fixtures — Creating reusable test data and test setup.
Test Database — Django creates a separate temporary database while running tests, preventing test data from affecting the development database.
Mocking — Replacing external dependencies or expensive operations with controlled test objects.
Outcome:
Understood when different testing techniques should be used and how Django's testing framework supports automated backend testing.

#Authentication Tests

Automated tests were created for the application's authentication functionality.
Test scenarios
User registration
Successful login
Invalid login credentials
Logout
Token refresh
Password change
Expired JWT token
Validation performed

The tests verify:
Correct HTTP status codes
Successful authentication responses
Access and refresh token generation
Invalid credentials handling
Refresh-token behavior after logout
Password update
Expired-token rejection
Result
Authentication functionality was successfully tested through automated tests.

#Permission Tests

Role-based access control was tested for different types of users.
Roles tested
Admin
Driver
Passenger/User
Anonymous user
Validation performed
The tests verified that:
Admin users can access admin-protected APIs.
Passenger/User accounts cannot access admin-only APIs.
Driver accounts cannot access admin-only APIs.
Anonymous users receive an authentication error when authentication is required.
Result
Role-based permissions were successfully validated through automated tests.

#Ride API Tests

Automated tests were implemented for the ride lifecycle.

Ride operations tested
Create Ride
     ↓
Accept Ride
     ↓
Start Ride
     ↓
Complete Ride

Additional lifecycle operation:

Cancel Ride
Invalid transitions
Tests were also created to ensure that invalid ride-status transitions are rejected.
Validation performed
The tests verified:
Ride creation
Driver assignment
Ride acceptance
Ride start
Ride completion
Ride cancellation
Invalid status transitions
Appropriate HTTP responses
Result
The ride lifecycle APIs were successfully tested.

#Business Logic Tests

The important ride-booking business rules were tested independently.
Areas tested
Fare Calculation
Verified the fare calculation functionality and expected fare values.
Driver Availability
Tested whether only available drivers can be assigned to rides.
Nearby Driver Selection
Tested driver selection based on geographical location.
Ride Validation
Verified that invalid ride data and invalid ride conditions are rejected.
Cancellation Rules
Tested cancellation behavior for rides in different states and verified that completed/cancelled rides cannot be cancelled again.
Result
Core ride-booking business logic was successfully tested.

#Database Tests

Database-level constraints and relationships were tested.
Areas tested
Model constraints
Unique fields
Foreign-key relationships
Required fields
Invalid relationships
Examples tested
Negative fare values are rejected.
Duplicate email addresses are rejected.
Required Ride.user relationships are enforced.
Invalid foreign-key relationships are detected.
Duplicate DriverProfile relationships are prevented.
Result
Database constraints and model relationships were successfully validated.

#WebSocket & Celery Tests

Real-time communication and asynchronous background tasks were tested.
WebSocket Testing
The following scenarios were tested:

Authentication
Valid rider connection
Valid driver connection
Missing token
Invalid token
Unauthorized user
Ride Status Events
Tested that ride-status changes are sent to the appropriate WebSocket group.
Driver Location Events
Tested that updated driver coordinates are broadcast through WebSocket.
The location event was verified using:

type
ride_id
latitude
longitude
Result

The WebSocket test suite completed successfully:

Ran 7 tests
OK

Celery Testing
Celery notification tasks were tested for:

Ride notifications
Driver assignment notifications
Ride completion notifications
Reminder notifications
Failed Task Retry

The retry mechanism was also tested.

The retry task follows this sequence:

Attempt 1 → Failed → Retry
Attempt 2 → Failed → Retry
Attempt 3 → Successful

The retry behavior was successfully validated.
Result
Celery task execution and retry behavior were successfully tested.

#Generate Test Report

The complete Django test suite was executed after completing the previous testing tasks.

Final Test Results
Total Tests : 98
Passed      : 98
Failed      : 0
Skipped     : 0
Coverage    : 86%

Test execution result:
Ran 98 tests in 252.313s
OK
Coverage Result
Coverage.py was used to measure the backend code coverage.

Statements : 1926
Missed     : 263
Coverage   : 86%
Final Status
All 98 automated tests passed successfully with zero failures.
Overall Work Summary

Today's work established a comprehensive automated testing foundation for the Django REST backend.

Task	Area	                     Status
Task 1	Django Testing Fundamentals	 ✅ Completed
Task 2	Authentication Tests	     ✅ Completed
Task 3	Permission Tests	         ✅ Completed
Task 4	Ride API Tests	             ✅ Completed
Task 5	Business Logic Tests	     ✅ Completed
Task 6	Database Tests	             ✅ Completed
Task 7	WebSocket & Celery Tests	 ✅ Completed
Task 8	Test Report & Coverage	     ✅ Completed
Final Outcome

The backend now has an automated test suite covering authentication, authorization, ride lifecycle, business rules, database integrity, real-time WebSocket events, Celery background tasks, and retry behavior.
Final result: 98/98 tests passed, 0 failed, 0 skipped, with 86% overall code coverage.




*****API Performance, Caching & Scalability Engineering

#Identify Critical APIs

Objective
Identified the APIs that are most important for the mobile ride-booking application.
Critical APIs identified
1. Login
2. Driver Location
3. Nearby Drivers
4. Create Ride
5. Ride Details
6. Ride History
7. Notifications
Work Completed
Reviewed these APIs based on their importance to the application's core ride-booking workflow.
Result
Critical APIs were identified for further performance monitoring and optimization.


#Establish Performance Baseline

Objective
Established an initial performance baseline before optimization.
Tool Used
Django Silk
Django Silk was configured to monitor API performance.
Metrics measured
Response time
Database query count
Database query time
API request frequency
CPU and memory monitoring using psutil
APIs tested

Examples included:
POST /accounts/login/
GET /api/rides/active/
GET /api/drivers/nearby/
PATCH /api/rides/<ride_id>/location/
POST /api/rides/<ride_id>/accept/
Example observed results

The Silk dashboard showed API-level measurements such as:
Nearby Drivers
Response Time: ~130 ms
Database Queries: 2
Database Time: ~13 ms
The exact values varied between requests during testing.
Result
A performance baseline was established to compare API behavior before and after optimization.


#Optimize Database Queries

Objective
Reviewed APIs for unnecessary database queries and optimized database access where appropriate.
Areas reviewed
N+1 query problems
Repeated queries
Missing indexes
Large responses
Related-object queries
Optimizations applied

Used Django ORM techniques where appropriate:
select_related()
prefetch_related()
values()
indexes
Existing database optimizations

Ride indexes were configured for commonly queried fields such as:
user + created_at
driver + created_at
status + created_at

Vehicle type queries were also supported by an index on:
vehicle_type
Field selection
Several list/history APIs use .values() to retrieve only the required fields instead of unnecessarily returning the complete model data.

Result
Database access was reviewed and optimized to reduce unnecessary queries and response data.


#Implement Redis Caching

Objective
Implemented Redis caching for frequently accessed, relatively static data.
Cached data
The primary caching example was:
Vehicle Types
Cache configuration
Django's cache backend was configured to use Redis:
redis://127.0.0.1:6379/1
The application uses a separate Redis database for caching, while Celery continues using Redis database 0.
Cache behavior
The Vehicle Type API:
GET /api/vehicle-types/
checks the cache before querying the database.

Conceptually:
Request
   ↓
Check Redis Cache
   ↓
Data exists?
 ┌───────┴───────┐
Yes             No
 ↓               ↓
Return Cache   Query DB
                 ↓
              Save Cache
                 ↓
              Return Data
Result
Redis caching was successfully tested and the cached data could be retrieved using Django's cache framework.


#Cache Invalidation

Objective
Ensured cached data is removed when the underlying data changes so that stale data is not served.
Cache invalidation flow
VehicleType Updated
        ↓
post_save Signal
        ↓
Delete "vehicle_types" Cache
        ↓
Next API Request
        ↓
Fetch Fresh Data
        ↓
Store New Cache
Implementation

A Django signal was configured through:
rides/apps.py
using:

def ready(self):
    from . import signals

The signal handles cache invalidation for VehicleType changes.

Testing

A stale-cache scenario was tested:

Cache = OLD DATA
        ↓
VehicleType updated
        ↓
Cache invalidated
        ↓
cache.get("vehicle_types")
        ↓
None
Result
Cache invalidation was implemented and tested to prevent stale Vehicle Type data.


#Pagination & Response Optimization

Objective
Optimized APIs that can return large amounts of data.
Pagination
The project already uses DRF pagination:

"DEFAULT_PAGINATION_CLASS":
"rest_framework.pagination.PageNumberPagination"

"PAGE_SIZE": 10

A dedicated large-dataset pagination configuration was also implemented:
Default page size: 20
Maximum page size: 100
Example
GET /api/rides/large-dataset/

Custom page size can be requested using:
?page_size=5
The maximum page size prevents clients from requesting an unnecessarily large response.
Field selection
Large/list APIs were reviewed to return only the fields required by the client.
Examples include:
id
pickup_address
drop_address
fare
created_at
Lightweight responses

A lightweight ride serializer was introduced for large/list responses to avoid returning unnecessary Ride fields.

Result
Pagination, field selection, lightweight responses, and maximum page-size protection were implemented/reviewed to improve API scalability.


#Load Testing

Objective
Simulated multiple users accessing the backend simultaneously and measured backend performance under load.
Tool Used
Locust
API tested
GET /api/rides/large-dataset/
Test configuration
Initial load test:
Number of users: 10
Ramp-up rate: 2 users/second
Host: http://127.0.0.1:8000
Metrics monitored
Requests/second
Average response time
Failure rate
Database load
Important test observation

The first Locust run produced:
100% failures
The Locust failure details showed:
ConnectionRefusedError(10061)
This was identified as a connectivity issue because the Django development server was not running/reachable at the time of that test.
The failed run was therefore not treated as the valid performance result.
Load-testing process
After ensuring the Django server was running:

Django Backend
      ↑
      │
   Locust
      │
 ┌────┼────┐
User User User
 1    2    3 ...

Locust was used to generate concurrent API requests and observe the backend's behavior.
Result
Load-testing infrastructure was successfully configured, and Locust was used to measure backend request performance.


#Performance Report

Before vs After Optimization
Area	                 Before Optimization	                                 After Optimization
Database queries	     Reviewed for unnecessary/repeated queries    select_related(), prefetch_related(), values() and indexes applied where appropriate
API responses	     Some APIs could return unnecessary fields  	  Field selection/lightweight responses introduced
Large datasets	         Risk of large responses	                     Pagination implemented
Page size	         No uncontrolled large page requests	Maximum page size of 100 for large-dataset API
Frequently accessed data  Database access on repeated requests	     Redis caching implemented
Stale cached data	  Potential stale data	                   Cache invalidation through signals
Performance monitoring	 Limited visibility                       	Django Silk configured
Load testing	           Manual testing              	Locust configured for concurrent users
Database monitoring     Basic observation    	Query count/time and PostgreSQL activity monitored

Performance Improvements
The main performance engineering improvements completed were:
Performance monitoring using Django Silk.
Database query optimization using appropriate ORM techniques.
Database indexing for frequently queried Ride fields.
Redis caching for Vehicle Type data.
Automatic cache invalidation when Vehicle Type data changes.
Pagination for large datasets.
Field selection and lightweight API responses.
Maximum page-size protection.
Load testing using Locust.
Response time, query count, failure rate and database activity monitoring.

Conclusion
The Django REST backend was reviewed from a performance and scalability perspective. Critical APIs were identified, baseline performance was measured using Django Silk, database queries were optimized, Redis caching and cache invalidation were implemented, and large responses were controlled using pagination and lightweight serializers. Finally, Locust was configured to simulate multiple concurrent users and evaluate backend behavior under load.
