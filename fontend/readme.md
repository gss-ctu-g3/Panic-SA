# Frontend

---

# Project Structure

```text
/public
│
├── index.html
├── contacts.html
├── history.html
├── notifications.html
├── admin.html
│
├── css/
│   ├── global.css
│   ├── panic.css
│   ├── contacts.css
│   ├── history.css
│   └── admin.css
│
├── js/
│   ├── api.js
│   ├── auth.js
│   ├── panic.js
│   ├── contacts.js
│   ├── history.js
│   ├── notifications.js
│   └── admin.js
│
└── components/
    ├── loader.js
    ├── modal.js
    ├── alerts.js
    └── badges.js
```

---

# Page 1: Panic Button

## File

```text
index.html
```

## Goal

Provide a one-tap emergency panic button that immediately sends an emergency alert with the user's GPS coordinates.

## API Integration

### Trigger Panic Alert

```http
POST /api/v1/alerts/panic
```

### Request Body

```json
{
  "userId": "user_123",
  "latitude": -26.12345,
  "longitude": 28.12345
}
```

## UI Components

### Panic Button| I am doing this part(Michelle Putter)


* [ ] Create large emergency button
* [ ] Style button for mobile devices
* [ ] Add disabled state during request

### Location Handling| I will do this part(Justin vd merwe)

* [ ] Request GPS permissions
* [ ] Capture latitude
* [ ] Capture longitude
* [ ] Handle permission denied errors

### Alert Submission

* [ ] Send request using Fetch API
* [ ] Show loading spinner
* [ ] Show success message
* [ ] Show error message

### Validation

* [ ] Prevent duplicate submissions
* [ ] Validate GPS coordinates before sending

---

# Page 2: Emergency Contacts

## File

```text
contacts.html
```

## Goal

Allow users to manage emergency contacts.

## API Integration

### Get Contacts| i will do this part Andipha Vundisa

```http
GET /api/v1/contacts/user/{userId}
```

### Create Contact

```http
POST /api/v1/contacts
```

### Update Contact

```http
PUT /api/v1/contacts/{contactId}
```

### Delete Contact

```http
DELETE /api/v1/contacts/{contactId}
```

## UI Components

### Contacts List

* [ ] Create contacts table
* [ ] Display name
* [ ] Display phone number
* [ ] Display email
* [ ] Display relationship

### Add Contact Form

* [ ] Name field
* [ ] Phone field
* [ ] Email field
* [ ] Relationship field

### Edit Contact Form

* [ ] Populate existing data
* [ ] Submit updates

### Delete Contact

* [ ] Add delete button
* [ ] Show confirmation modal
* [ ] Refresh contact list

### Validation

* [ ] Validate phone number
* [ ] Validate email address
* [ ] Validate required fields

---

# Page 3: Alert History

## File

```text
history.html
```

## Goal

Allow users to view previously submitted emergency alerts.

## API Integration

### Get Alert History

```http
GET /api/v1/alerts/user/{userId}
```

## UI Components

### Alert List

Display:

* Alert ID
* Date
* Time
* Status

### Tasks

* [ ] Fetch alert history
* [ ] Render alert cards/table
* [ ] Sort newest first
* [ ] Create empty-state message
* [ ] Add loading state
* [ ] Handle API failures

---

# Page 4: Notification History

## File

```text
notifications.html
```

## Goal

Display notification delivery records.

## API Integration

### Get Notifications

```http
GET /api/v1/history/notifications?userId={userId}
```

## UI Components

Display:

* Channel
* Recipient
* Status
* Date Sent

### Tasks

* [ ] Fetch notification logs
* [ ] Display SMS notifications
* [ ] Display Email notifications
* [ ] Create status badges
* [ ] Add loading state
* [ ] Handle API errors

---

# Page 5: Admin Dashboard| I am doing this part (Michelle Putter)

## File

```text
admin.html
```

## Goal

Provide administrators with realtime emergency alert monitoring.

## API Integration

### Active Alerts

```http
GET /api/v1/admin/alerts/active
```

### Statistics

```http
GET /api/v1/admin/stats
```

### Realtime Stream

```http
GET /api/v1/admin/alerts/stream
```

## UI Components

### Statistics Cards

Display:

* Total Alerts
* Today's Alerts
* Active Alerts

### Active Alerts Table

Display:

* Alert ID
* User ID
* Latitude
* Longitude
* Status
* Timestamp

### Realtime Updates

* [ ] Connect to SSE/WebSocket
* [ ] Receive new alerts
* [ ] Update dashboard automatically
* [ ] Show connection status

### Tasks

* [ ] Create statistics section
* [ ] Create active alerts table
* [ ] Fetch active alerts
* [ ] Fetch statistics
* [ ] Subscribe to realtime stream
* [ ] Handle stream disconnects
* [ ] Handle API failures

---

# Shared JavaScript Modules

## api.js

### Tasks

* [ ] Create API base URL configuration
* [ ] Create GET helper
* [ ] Create POST helper
* [ ] Create PUT helper
* [ ] Create DELETE helper
* [ ] Centralize error handling

---

## auth.js

### Tasks

* [ ] Store authenticated user ID
* [ ] Retrieve user session
* [ ] Handle logout
* [ ] Protect admin page access

---

# Shared UI Components

## Loader Component

* [ ] Create reusable loading spinner
* [ ] Show during API requests

## Alert Component

* [ ] Success notifications
* [ ] Error notifications
* [ ] Warning notifications

## Modal Component

* [ ] Confirmation dialog
* [ ] Delete confirmation modal

## Badge Component

* [ ] Delivered
* [ ] Failed
* [ ] Pending
* [ ] Active

---

# Styling

## Global Styling

* [ ] Responsive layout
* [ ] Mobile-first design
* [ ] Accessibility improvements
* [ ] Consistent color palette

## Panic Button Styling

* [ ] Large emergency button
* [ ] High visibility colors
* [ ] Touch-friendly sizing

## Admin Dashboard Styling

* [ ] Responsive tables
* [ ] Statistics cards
* [ ] Status indicators

---

# The frontend is considered complete when:

* [ ] Panic alert page works
* [ ] GPS location is captured successfully
* [ ] Contacts can be created, edited and deleted
* [ ] Alert history is visible
* [ ] Notification history is visible
* [ ] Admin dashboard displays active alerts
* [ ] Realtime updates function correctly
* [ ] All API integrations are complete
* [ ] Mobile responsiveness is implemented
* [ ] Error handling is implemented
