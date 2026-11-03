# Vehicle Service Management System

A custom Frappe application built on **Frappe Framework** and **ERPNext** to manage vehicle servicing operations: customer vehicles, service bookings, technician assignments, job cards, service task tracking, and automated completion workflows.

---

## 1. Overview & Architecture

This application extends ERPNext to provide an end-to-end service workflow for automotive workshops and service centers.

```
+-------------------------------------------------------------------+
|                     Vehicle Service Workflow                      |
+-------------------------------------------------------------------+
                                  |
                                  v
                       [Customer Vehicle]
             (Linked to standard ERPNext Customer)
                                  |
                                  v
                       [Service Booking]
            - Date & Conflict validations
            - Status: Draft -> Confirmed -> In Progress -> Completed
                                  |
                                  v
                      [Service Job Card]
            - Linked to Service Booking & Technician
            - Child Table: Job Card Task (task line items)
            - Auto-calculates Estimated Cost
            - Blocks completion until all tasks are marked Completed
            - Auto-updates linked Service Booking to "Completed"
```

### Standard ERPNext Reuse
- **`Customer`**: Standard ERPNext CRM/Selling DocType is directly linked for vehicle ownership and service billing.
- **`User` / `Employee`**: Standard Frappe User/Employee DocType is linked for assigning technicians.

---

## 2. DocTypes & Schema

### 1. `Customer Vehicle` (Master DocType)
* **Fields**:
  * `customer` (`Link` -> `Customer`): Vehicle owner.
  * `registration_number` (`Data`): License plate number (Unique index).
  * `make` (`Data`): e.g., Toyota, Hyundai.
  * `model` (`Data`): e.g., Innova, Creta.
  * `year` (`Int`): Model year.
  * `notes` (`Small Text`): Additional vehicle notes.
* **Controller Validations**:
  * Strips whitespace and standardizes registration number to uppercase.
  * Prevents duplicate vehicle registrations using `frappe.db.exists`.

### 2. `Service Booking` (Transaction DocType)
* **Fields**:
  * `customer` (`Link` -> `Customer`): Mandatory.
  * `vehicle` (`Link` -> `Customer Vehicle`): Mandatory.
  * `booking_date` (`Datetime`): Scheduled appointment date and time.
  * `service_type` (`Select`): Periodic Maintenance, Oil Change, Brake Inspection, General Service, Engine Diagnostics, Body & Paint, Other.
  * `status` (`Select`): Draft, Confirmed, In Progress, Completed, Cancelled (Default: Draft).
  * `notes` (`Small Text`): Customer instructions.
* **Controller Validations**:
  * **Ownership Check**: Ensures the selected vehicle belongs to the chosen customer.
  * **Past Date Prevention**: Prevents scheduling appointments in the past.
  * **Conflict Prevention**: Prevents scheduling another active booking for the same vehicle at the exact same date and time.

### 3. `Job Card Task` (Child Table DocType)
* **Fields**:
  * `task_name` (`Data`): Mandatory name of service task.
  * `description` (`Small Text`): Task description.
  * `status` (`Select`): Pending, In Progress, Completed (Default: Pending).
  * `estimated_cost` (`Currency`): Cost of the task.

### 4. `Service Job Card` (Execution DocType)
* **Fields**:
  * `service_booking` (`Link` -> `Service Booking`): Linked booking.
  * `customer` (`Link` -> `Customer`, Read Only): Auto-fetched from booking.
  * `vehicle` (`Link` -> `Customer Vehicle`, Read Only): Auto-fetched from booking.
  * `assigned_technician` (`Link` -> `User`): Technician assigned to work.
  * `tasks` (`Table` -> `Job Card Task`): Child table of tasks.
  * `estimated_cost` (`Currency`): Auto-calculated total from child table tasks.
  * `actual_cost` (`Currency`): Final billed amount (auto-defaults to estimated cost).
  * `status` (`Select`): Open, In Progress, Completed, Cancelled.
  * `remarks` (`Small Text`): Work remarks.
* **Controller & UI Logic**:
  * `calculate_estimated_cost()`: Automatically calculates the sum of all task costs on save and live via Client Script.
  * `validate_task_completion()`: Blocks marking a Job Card as "Completed" if any child task is still "Pending" or "In Progress".
  * `sync_booking_status()`: Lifecycle hook (`on_update`) that automatically updates the linked `Service Booking` to **Completed** when the Job Card is completed.

---

## 3. REST API Reference

All custom APIs are defined in `vehicle_service_management/api/booking.py` using `@frappe.whitelist()`.

### 1. Create Service Booking
* **Method**: `POST`
* **URL**: `/api/method/vehicle_service_management.api.booking.create_booking`
* **Payload**:
  ```json
  {
      "customer": "John Doe",
      "vehicle": "KL-07-AB-1234",
      "booking_date": "2026-11-05 10:30:00",
      "service_type": "Periodic Maintenance",
      "notes": "Regular 10,000 km general service"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
      "message": {
          "name": "SB-2026-00001",
          "customer": "John Doe",
          "vehicle": "KL-07-AB-1234",
          "booking_date": "2026-11-05 10:30:00",
          "service_type": "Periodic Maintenance",
          "status": "Draft"
      }
  }
  ```

### 2. Retrieve Booking Details
* **Method**: `GET`
* **URL**: `/api/method/vehicle_service_management.api.booking.get_booking?booking_id=SB-2026-00001`
* **Response (200 OK)**:
  Returns full document details.
* **Response (404 Not Found)**:
  If `booking_id` does not exist:
  ```json
  {
      "exc_type": "DoesNotExistError",
      "message": "Service Booking SB-XXXXX not found!"
  }
  ```

### 3. Update Booking Status
* **Method**: `POST`
* **URL**: `/api/method/vehicle_service_management.api.booking.update_booking_status`
* **Payload**:
  ```json
  {
      "booking_id": "SB-2026-00001",
      "status": "Confirmed"
  }
  ```
* **Validation**: Validates that the requested status is one of: `["Draft", "Confirmed", "In Progress", "Completed", "Cancelled"]`.

---

## 4. Roles & Permissions

| DocType | Administrator / System Manager | Service Advisor | Technician |
| :--- | :---: | :---: | :---: |
| **Customer Vehicle** | Full Access (CRUD) | Create, Read, Write, Delete | Read Only |
| **Service Booking** | Full Access (CRUD) | Create, Read, Write, Delete | Read Only |
| **Service Job Card** | Full Access (CRUD) | Create, Read, Write, Delete | Read & Write (Update tasks/status) |

---

## 5. Installation & Setup

### Option A: Standard Frappe Bench
```bash
# 1. Clone the app repository
cd /path/to/frappe-bench
bench get-app https://github.com/thereal4ne/vehicle_service_management.git

# 2. Install the app onto your site
bench --site [sitename] install-app vehicle_service_management

# 3. Run database migrations to sync DocTypes
bench --site [sitename] migrate

# 4. Clear cache
bench --site [sitename] clear-cache
```

### Option B: Docker Setup (frappe_docker)
```powershell
# 1. Copy repository into backend container
docker cp "vehicle_service_management" frappe_docker-backend-1:/home/frappe/frappe-bench/apps/

# 2. Install app onto the site
docker exec -it frappe_docker-backend-1 bench --site frontend install-app vehicle_service_management

# 3. Run migration and clear cache
docker exec -it frappe_docker-backend-1 bench --site frontend migrate
docker exec -it frappe_docker-backend-1 bench --site frontend clear-cache
```

---

## 6. End-to-End Workflow Demonstration

1. **Create Customer**: Open Desk -> Search `Customer` -> Create customer (e.g., `John Doe`).
2. **Create Vehicle**: Search `Customer Vehicle` -> Select `John Doe`, enter Registration Number `KL-07-AB-1234`, Make `Toyota`, Model `Innova`.
3. **Create Service Booking**:
   * Pick `Customer`: `John Doe`.
   * Pick `Vehicle`: `KL-07-AB-1234`.
   * Set appointment date (future date).
   * Pick Service Type: `Periodic Maintenance`.
   * Save (Status defaults to `Draft`).
4. **Create Service Job Card**:
   * Pick the `Service Booking`. Notice Customer and Vehicle are auto-fetched!
   * Assign a `Technician` (User).
   * Add tasks to the Child Table:
     * Task 1: "Engine Oil Replacement", Cost: 2500, Status: `Completed`.
     * Task 2: "Oil Filter Change", Cost: 500, Status: `Completed`.
   * Notice **Estimated Cost** and **Actual Cost** auto-calculate to `3000.00`!
   * Change Job Card status to `Completed` and Save.
5. **Verify Automation**:
   * Open the linked `Service Booking` -> Notice its status is automatically updated to **`Completed`**!

---

## 7. Testing with Postman

1. Open Postman.
2. Click **Import** -> Select `Vehicle_Service_Management.postman_collection.json`.
3. Set the collection variable `base_url` to your server (e.g., `http://localhost:8080`).
4. Run request `1. Authentication (Login)` with your admin credentials to establish the session.
5. Execute the endpoints to test booking creation, retrieval, updates, and validation error cases.
