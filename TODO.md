# Panic SA

A web-based emergency response system that allows users to trigger a panic alert with a single click, automatically notifying emergency contacts via SMS and email while providing administrators with a live dashboard of incoming alerts.

---

# Core Features

## Panic Alerts

Users can trigger an emergency alert using a single button.

The system will:

1. Capture the user's GPS coordinates
2. Create an alert record
3. Send SMS notifications to emergency contacts
4. Send email notifications to emergency contacts
5. Log the alert
6. Display the alert on the admin dashboard

---

## Emergency Contacts

Users can:

* Add contacts
* View contacts
* Update contacts
* Delete contacts

Each contact may contain:

* Name
* Phone Number
* Email Address
* Relationship

---

## Alert History

Users can view:

* Previous alerts
* Alert timestamps
* Delivery status
* Notification history

---

## Admin Dashboard

Administrators can:

* View active alerts
* Monitor incoming alerts in realtime
* Filter alerts
* View alert statistics
* Monitor delivery status

---

# Technology Stack

## Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* Fetch API
* WebSockets

## Backend

REST API Services:

* Alert Service
* Contact Management Service
* SMS Service
* Email Service
* Admin Service

## Database

Suggested:

* PostgreSQL
* MySQL
* SQLite (development)

---

# Project Structure

```text
frontend/
│
├── index.html
├── contacts.html
├── history.html
├── admin.html
│
├── css/
├── js/
└── assets/

backend/
│
├── alert-service/
├── contact-service/
├── sms-service/
├── email-service/
└── admin-service/

docs/
│
├── TODO_FRONTEND.md
├── TODO_BACKEND.md
└── examples/
```

---

# API Base URL

```text
https://gss-panic-api.pixieoflife.co.za
```

---

# Main API Endpoints

## Panic Alert

```http
POST /api/v1/alerts/panic
```

Creates a new emergency alert.

---

## Contacts

```http
GET    /api/v1/contacts/user/{userId}
POST   /api/v1/contacts
PUT    /api/v1/contacts/{contactId}
DELETE /api/v1/contacts/{contactId}
```

---

## Alert History

```http
GET /api/v1/alerts/user/{userId}
```

---

## Notification History

```http
GET /api/v1/history/notifications
```

---

## Admin Dashboard

```http
GET /api/v1/admin/alerts/active
GET /api/v1/admin/stats
GET /api/v1/admin/alerts/stream
```

---

# Development Workflow

## Frontend Team

Responsible for:

* User Interface
* GPS Integration
* API Consumption
* Responsive Design
* Realtime Dashboard Updates

See:

```text
docs/TODO_FRONTEND.md
```

---

## Backend Team

Responsible for:

* REST APIs
* SMS Delivery
* Email Delivery
* Alert Processing
* Database Management
* Realtime Alert Streaming

See:

```text
docs/TODO_BACKEND.md
```

---

# Examples

Task format used throughout project documentation:

```text
- [ ] Task not started
- [x] Task completed
- [ ] Task in progress | developer-name
```

Example:

```text
- [ ] Create panic button page
- [x] Configure API client
- [ ] Build admin dashboard | john
```

---

#The project is complete when:

* [ ] Panic alerts can be triggered
* [ ] GPS coordinates are captured correctly
* [ ] SMS notifications are delivered
* [ ] Email notifications are delivered
* [ ] Emergency contacts can be managed
* [ ] Alert history is accessible
* [ ] Admin dashboard receives realtime updates
* [ ] Mobile responsiveness is complete
* [ ] API documentation is available
* [ ] Deployment is complete
