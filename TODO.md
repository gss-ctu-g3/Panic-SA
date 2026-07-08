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

## Emergency Contacts

Users can add, view, update, and delete emergency contacts (name, phone, email, relationship).

## Alert History

Users can view previous alerts with timestamps and status.

## Admin Dashboard

Administrators can view active alerts, filter by status, and see alert statistics.

## Live Alert Page

Public page at `/alert/live/{alertId}` linked from SMS messages.

---

# Technology Stack

## Frontend

* HTML5, CSS3, Vanilla JavaScript
* Fetch API
* Tailwind CDN (main app pages)

## Backend

* FastAPI microservices (Python)
* MongoDB
* nginx reverse proxy
* Docker Compose

## Services

* User Management
* Contact Management
* Alert Service
* SMS Service (BulkSMS)
* Email Service (Mailgun)
* History Service
* Admin Service

---

# Project Structure

```text
fontend/public/
├── index.html
├── login.html
├── register.html
├── contacts.html
├── history.html
├── admin.html
├── alert/live.html
├── css/
├── js/
└── components/

backend/python/
├── user_management_service/
├── contact_management_service/
├── alert_service/
├── sms_service/
├── email_service/
├── history_service/
└── admin_service/

nginx/
docker-compose.yml
.env.example
```

---

# API Routes (via nginx)

## Authentication

```http
POST /auth/login
POST /auth/signup
```

## Contacts

```http
GET    /contacts/user/{userId}
GET    /contacts/{contactId}
POST   /contacts
PUT    /contacts/{contactId}
DELETE /contacts/{contactId}
```

## Alerts

```http
POST  /alerts/panic
GET   /alerts/active/me
GET   /alerts/{alertId}
PATCH /alerts/{alertId}/location
POST  /alerts/{alertId}/cancel
```

## History

```http
GET /history/alerts/user/{userId}
```

## Admin

```http
GET /admin/alerts
GET /admin/alerts?status={status}
GET /admin/stats
```

## Planned (not implemented)

```http
GET  /history/notifications
GET  /admin/alerts/stream
POST /sms/webhook
POST /email/webhook
```

---

# Documentation

* Frontend details: `fontend/readme.md`
* Backend details: `backend/readme.md`

---

# The project is complete when:

* [x] Panic alerts can be triggered
* [x] GPS coordinates are captured correctly
* [x] SMS notifications are delivered
* [x] Email notifications are delivered
* [x] Emergency contacts can be managed
* [x] Alert history is accessible
* [x] Admin dashboard displays alerts and stats
* [x] Login, register, and live alert pages work
* [ ] Admin dashboard receives realtime updates
* [ ] Notification history is available
* [x] Mobile responsiveness is largely complete
* [ ] API documentation is published
* [ ] Deployment is complete
