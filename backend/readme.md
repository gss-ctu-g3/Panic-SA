# Backend

FastAPI microservices under `backend/python/`, orchestrated by `docker-compose.yml` and proxied through nginx.

Each service uses a `schemas.py` for FastAPI request/response models.

---

# Services

| Service | Folder | nginx route |
|---------|--------|-------------|
| User Management | `user_management_service` | `/auth/` |
| Contact Management | `contact_management_service` | `/contacts`, `/contacts/` |
| Alert | `alert_service` | `/alerts/` |
| SMS | `sms_service` | `/sms/` |
| Email | `email_service` | `/email/` |
| History | `history_service` | `/history/` |
| Admin | `admin_service` | `/admin/` |

---

# Phase 1: Project Setup

## Core Setup

* [x] Initialize backend project
* [x] Configure environment variables (`.env.example`)
* [x] Setup database connection (MongoDB)
* [x] Configure authentication (JWT)
* [x] Docker Compose and nginx wiring
* [ ] Setup structured logging
* [ ] Rate limiting

---

# Phase 2: Database Design

MongoDB database: `panic_sa`

## Collections

* [x] `users` — authentication and profiles
* [x] `contacts` — emergency contacts linked to users
* [x] `alerts` — GPS coordinates, status, timestamps
* [x] SMS delivery logs in `sms` database (`logs` collection)

---

# Phase 3: User Management Service

Base URL: `/auth`

## Endpoints

* [x] `POST /auth/signup`
* [x] `POST /auth/login`

---

# Phase 4: Contact Management Service

Base URL: `/contacts`

## Endpoints

* [x] `POST /contacts`
* [x] `GET /contacts/user/{user_id}`
* [x] `GET /contacts/{contact_id}`
* [x] `PUT /contacts/{contact_id}`
* [x] `DELETE /contacts/{contact_id}`

## Validation

* [x] Validate phone numbers
* [x] Validate email addresses
* [x] Limit maximum contacts per user

---

# Phase 5: SMS Service

Base URL: `/sms`

Provider: BulkSMS

## Endpoints

* [x] `POST /sms/bulk` — used by alert service
* [x] `POST /sms/send` — implemented, not wired by other services
* [ ] `POST /sms/webhook`

---

# Phase 6: Email Service

Base URL: `/email`

Provider: Mailgun

## Endpoints

* [x] `POST /email/alert` — used by alert service
* [x] `POST /email/consent` — implemented, not wired by other services
* [ ] `POST /email/webhook`

## Templates

* [x] `templates/alert.html`
* [x] `templates/consent.html`

---

# Phase 7: Alert Service

Base URL: `/alerts`

## Endpoints

* [x] `POST /alerts/panic`
* [x] `GET /alerts/active/me`
* [x] `GET /alerts/{alert_id}`
* [x] `PATCH /alerts/{alert_id}/location`
* [x] `POST /alerts/{alert_id}/cancel`

## Panic Flow

When panic button is pressed:

* [x] Validate user (JWT)
* [x] Capture GPS coordinates
* [x] Create alert record
* [x] Fetch emergency contacts
* [x] Send SMS notifications (bulk)
* [x] Send email notifications
* [ ] Notify admin dashboard in realtime

---

# Phase 8: History Service

Base URL: `/history`

## Endpoints

* [x] `GET /history/alerts/user/{user_id}` — response model in `schemas.py`

## Planned

* [ ] `GET /history/notifications`
* [ ] Pagination and date/status filters

---

# Phase 9: Admin Service

Base URL: `/admin`

## Endpoints

* [x] `GET /admin/alerts`
* [x] `GET /admin/alerts?status={status}`
* [x] `GET /admin/stats`

## Planned

* [ ] `GET /admin/alerts/stream` — realtime feed

---

# Phase 10: Security

* [x] JWT authentication
* [x] Admin role authorization
* [x] Request validation via Pydantic schemas
* [ ] Rate limiting
* [ ] Secure webhook validation

---

# Phase 11: Testing

* [ ] Unit tests per service
* [ ] Integration tests for panic workflow
* [ ] Load testing for bulk notifications

---

# Environment Variables

See `.env.example` for required values:

* `ENV_MONGO_URI`
* `ENV_JWT_SECRET`
* `MAX_CONTACTS_PER_USER`
* SMS and Mailgun credentials
* Inter-service URLs

---

# The backend is considered complete when:

* [x] Users can register and log in
* [x] Users can manage emergency contacts
* [x] Panic button triggers alert
* [x] GPS coordinates are stored
* [x] SMS notifications are sent
* [x] Email notifications are sent
* [x] Alert history is available
* [x] Admin can view alerts and stats
* [ ] Notification history endpoint exists
* [ ] Realtime admin stream exists
* [ ] All REST endpoints are documented
* [ ] Production deployment completed
