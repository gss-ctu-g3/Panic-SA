# Frontend

Static HTML/CSS/JS frontend served by nginx from `fontend/public/`.

---

# Project Structure

```text
fontend/public/
│
├── index.html
├── login.html
├── register.html
├── contacts.html
├── history.html
├── admin.html
├── alert/
│   └── live.html
│
├── css/
│   ├── global.css
│   ├── nav-menu.css
│   ├── panic.css
│   ├── login.css
│   ├── register.css
│   ├── contacts.css
│   ├── history.css
│   ├── admin.css
│   └── live-alert.css
│
├── js/
│   ├── api.js
│   ├── auth.js
│   ├── auth-guard.js
│   ├── login.js
│   ├── register.js
│   ├── panic.js
│   ├── contacts.js
│   ├── history.js
│   ├── admin.js
│   ├── live-alert.js
│   └── tailwind-config.js
│
└── components/
    └── nav-menu.js
```

---

# API Base URL

The frontend uses relative paths proxied by nginx (see `fontend/public/js/api.js`).

```text
/auth/
/contacts/
/alerts/
/history/
/admin/
```

---

# Page 1: Panic Button

## File

```text
index.html
```

## Goal

Provide a one-tap emergency panic button that sends an alert with the user's GPS coordinates.

## API Integration

```http
POST /alerts/panic
GET  /alerts/active/me
PATCH /alerts/{alertId}/location
POST /alerts/{alertId}/cancel
```

## Status

* [x] Large emergency button
* [x] GPS capture and permission handling
* [x] Active alert detection and location updates
* [x] Cancel active alert flow
* [x] Loading and error states
* [x] Auth guard and shared nav menu

---

# Page 2: Login and Register

## Files

```text
login.html
register.html
```

## API Integration

```http
POST /auth/login
POST /auth/signup
```

## Status

* [x] Login form with JWT session storage
* [x] Registration form
* [x] Redirect to panic page after login

---

# Page 3: Emergency Contacts

## File

```text
contacts.html
```

## API Integration

```http
GET    /contacts/user/{userId}
GET    /contacts/{contactId}
POST   /contacts
PUT    /contacts/{contactId}
DELETE /contacts/{contactId}
```

## Status

* [x] List contacts
* [x] Create, edit, and delete contacts
* [x] Form validation and error handling
* [x] Auth guard and shared nav menu

---

# Page 4: Alert History

## File

```text
history.html
```

## API Integration

```http
GET /history/alerts/user/{userId}
```

## Status

* [x] Fetch and render alert history
* [x] Sort newest first
* [x] Empty state and loading handling
* [x] Auth guard and shared nav menu

---

# Page 5: Admin Dashboard

## File

```text
admin.html
```

## API Integration

```http
GET /admin/alerts
GET /admin/alerts?status={status}
GET /admin/stats
```

## Status

* [x] Statistics cards
* [x] Active alerts table with status filter
* [x] Admin-only nav link and auth guard
* [ ] Realtime stream (`GET /admin/alerts/stream`) — not implemented

---

# Page 6: Live Alert (Public)

## File

```text
alert/live.html
```

Served by nginx at `/alert/live/{alertId}`.

## API Integration

```http
GET /alerts/{alertId}
```

## Status

* [x] Public read-only alert view for SMS links
* [x] Map embed and alert details
* [x] No auth required

---

# Shared JavaScript Modules

## api.js

* [x] API base URL configuration
* [x] GET, POST, PUT, PATCH, DELETE helpers
* [x] Centralized auth header and error handling

## auth.js

* [x] JWT session storage
* [x] Login/logout helpers
* [x] Admin role detection

## auth-guard.js

* [x] Redirect unauthenticated users to login

## components/nav-menu.js

* [x] Shared navigation across authenticated pages
* [x] Admin-only link visibility

---

# Styling

* [x] Tailwind CDN on main app pages (`tailwind-config.js`)
* [x] Standalone CSS for login/register
* [x] Shared global and nav-menu styles
* [x] Mobile-friendly layouts

---

# Still Pending

* [ ] Realtime admin dashboard updates (SSE/WebSocket)
* [ ] Notification delivery history page (removed; no backend endpoint yet)

---

# The frontend is considered complete when:

* [x] Panic alert page works
* [x] GPS location is captured successfully
* [x] Contacts can be created, edited and deleted
* [x] Alert history is visible
* [x] Admin dashboard displays alerts and stats
* [x] Login, register, and live alert pages work
* [x] API integrations are complete for implemented endpoints
* [x] Mobile responsiveness is implemented
* [x] Error handling is implemented
* [ ] Realtime updates function correctly
