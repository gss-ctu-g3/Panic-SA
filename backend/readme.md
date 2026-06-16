# Backend

---

# Phase 1: Project Setup

## Core Setup

* [ ] Initialize backend project
* [ ] Configure environment variables
* [ ] Setup database connection
* [ ] Configure authentication (JWT)
* [ ] Setup logging
* [ ] Setup validation middleware
* [ ] Setup API documentation (Swagger/OpenAPI)

---

# Phase 2: Database Design | Mthokozisi Vundla

## Users Table | Mthokozisi Vundla

* [ ] Create users table
* [ ] Add authentication fields
* [ ] Add timestamps

## Emergency Contacts Table | Mthokozisi Vundla

* [ ] Create emergency_contacts table
* [ ] Link contact to user
* [ ] Store:

  * [ ] Name
  * [ ] Phone number
  * [ ] Email
  * [ ] Relationship

## Alerts Table | Mthokozisi Vundla

* [ ] Create alerts table
* [ ] Store GPS coordinates
* [ ] Store alert status
* [ ] Store timestamps

## Notification Logs Table | Mthokozisi Vundla

* [ ] Create notification_logs table
* [ ] Store channel type

  * [ ] SMS
  * [ ] EMAIL
* [ ] Store delivery status
* [ ] Store provider response

---

# Phase 3: Contact Management Service | Mthokozisi Vundla

Base URL:

/api/v1/contacts

## Endpoints

### Create Contact | Mthokozisi Vundla

* [ ] POST /contacts

### Get User Contacts | Mthokozisi Vundla

* [ ] GET /contacts/user/{userId}

### Get Single Contact | Mthokozisi Vundla

* [ ] GET /contacts/{contactId}

### Update Contact | Mthokozisi Vundla

* [ ] PUT /contacts/{contactId}

### Delete Contact | Mthokozisi Vundla

* [ ] DELETE /contacts/{contactId}
## Validation

* [ ] Validate phone numbers
* [ ] Validate email addresses
* [ ] Limit maximum contacts per user

---

# Phase 4: SMS Service

Base URL:

/api/v1/sms

## Provider Integration

* [ ] Integrate Africa's Talking
* [ ] OR Integrate Twilio

## Endpoints

### Send SMS

* [ ] POST /sms/send

### Bulk SMS

* [ ] POST /sms/bulk

### Delivery Webhook

* [ ] POST /sms/webhook

## Features

* [ ] Queue outgoing SMS
* [ ] Handle failures
* [ ] Retry failed messages
* [ ] Log provider responses

---

# Phase 5: Email Service | c.Scholtz 

Base URL: | c.Scholtz 

/api/v1/emails | c.Scholtz 

## Provider Integration | c.Scholtz 
* [ ] SMTP
* [ ] OR SendGrid
* [ ] OR SES

## Endpoints | c.Scholtz 

### Send Email | c.Scholtz 

* [ ] POST /emails/send

### Delivery Webhook | c.Scholtz 

* [ ] POST /emails/webhook

## Features | c.Scholtz 

* [ ] Generate HTML email template
* [ ] Generate Google Maps link
* [ ] Track delivery status
* [ ] Log provider responses

---

# Phase 6: Alert Service Lesedi.R 

Base URL:

/api/v1/alerts

## Endpoints Lesedi Ramolotja

### Trigger Panic Alert Lesedi Ramolotja

* [ ] POST /alerts/panic

### Get Alert Lesedi Ramolotja

* [ ] GET /alerts/{alertId}

### User Alert History Lesedi Ramolotja

* [ ] GET /alerts/user/{userId}

## Panic Flow Lesedi Ramolotja

When panic button is pressed:

* [ ] Validate user
* [ ] Capture GPS coordinates
* [ ] Create alert record
* [ ] Fetch emergency contacts
* [ ] Generate Google Maps URL
* [ ] Send SMS notifications
* [ ] Send email notifications
* [ ] Store notification logs
* [ ] Notify admin dashboard
* [ ] Return success response

---

# Phase 7: History Service | Dylan Van Der Velde

Base URL:

/api/v1/history

## Endpoints

### Alert History

* [ ] GET /history/alerts

### Notification History

* [ ] GET /history/notifications

## Features

* [ ] Filter by user
* [ ] Filter by date
* [ ] Filter by status
* [ ] Pagination support

---

# Phase 8: Admin Dashboard API

Base URL:

/api/v1/admin

## Endpoints

### Active Alerts

* [ ] GET /admin/alerts/active

### Alert Statistics

* [ ] GET /admin/stats

### Live Alert Feed

* [ ] GET /admin/alerts/stream

## Features

* [ ] Real-time alert updates
* [ ] Active alert count
* [ ] Daily alert count
* [ ] Alert status monitoring

---

# Phase 9: Security | Dylan Van Der Velde

* [ ] JWT authentication
* [ ] Role-based access control
* [ ] Admin authorization
* [ ] Request validation
* [ ] Rate limiting
* [ ] Input sanitization
* [ ] Secure webhook validation

---

# Phase 10: Testing

## Unit Tests

* [ ] Contact service tests
* [ ] SMS service tests
* [ ] Email service tests
* [ ] Alert service tests

## Integration Tests

* [ ] SMS provider integration
* [ ] Email provider integration
* [ ] Panic alert workflow

## Load Testing

* [ ] Multiple simultaneous alerts
* [ ] Bulk notification testing

---

# The project is considered complete when:

* [ ] Users can manage emergency contacts
* [ ] Panic button triggers alert
* [ ] GPS coordinates are stored
* [ ] SMS notifications are sent
* [ ] Email notifications are sent
* [ ] Alert history is available
* [ ] Admin can view active alerts
* [ ] All REST endpoints are documented
* [ ] Production deployment completed
