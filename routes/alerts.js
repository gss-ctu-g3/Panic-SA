// routes/alerts.js
const express = require('express');
const router = express.Router();
const authenticate = require('../middleware/authenticate');
const Alert = require('../models/Alert');
const EmergencyContact = require('../models/EmergencyContact');
const NotificationLog = require('../models/NotificationLog');
const { sendSMS, sendEmail } = require('../services/notifications');

// POST /api/panic
router.post('/panic', authenticate, async (req, res) => {
  try {
    const userId = req.user.id;
    const { latitude, longitude } = req.body;

    if (!latitude || !longitude) {
      return res.status(400).json({ success: false, message: 'Latitude and longitude are required' });
    }

    const alert = await Alert.create({
      userId,
      latitude,
      longitude,
      status: 'active'
    });

    console.log('Created alert:', alert._id);

    const contacts = await EmergencyContact.find({ userId });
    const mapsUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;

    for (let contact of contacts) {
      if (contact.phone) {
        const smsResult = await sendSMS(contact.phone, `Emergency alert! Location: ${mapsUrl}`);
        await NotificationLog.create({
          alertId: alert._id,
          userId,
          contactName: contact.name,
          channel: 'sms',
          recipient: contact.phone,
          status: smsResult.success ? 'sent' : 'failed'
        });
      }
      if (contact.email) {
        const emailResult = await sendEmail(contact.email, 'Emergency Alert', `Location: ${mapsUrl}`);
        await NotificationLog.create({
          alertId: alert._id,
          userId,
          contactName: contact.name,
          channel: 'email',
          recipient: contact.email,
          status: emailResult.success ? 'sent' : 'failed'
        });
      }
    }

    const io = req.app.get('io');
    io.to('emergency-responders').emit('new-panic-alert', {
      alertId: alert._id,
      userId,
      latitude,
      longitude,
      mapsUrl,
      timestamp: alert.createdAt
    });

    return res.status(200).json({ success: true, message: 'Panic alert triggered', alertId: alert._id });
  } catch (err) {
    console.log('Error in panic route:', err.message);
    return res.status(500).json({ success: false, message: 'Server error' });
  }
});

// GET /api/alerts/:alertId
router.get('/alerts/:alertId', authenticate, async (req, res) => {
  try {
    const { alertId } = req.params;
    const alert = await Alert.findById(alertId);

    if (!alert) {
      return res.status(404).json({ success: false, message: 'Alert not found' });
    }

    return res.status(200).json({ success: true, alert });
  } catch (err) {
    console.log('Error fetching alert:', err.message);
    return res.status(500).json({ success: false, message: 'Server error' });
  }
});

// GET /api/alerts/user/:userId
router.get('/alerts/user/:userId', authenticate, async (req, res) => {
  try {
    const { userId } = req.params;
    const { limit = 20, status } = req.query;

    const filter = { userId };
    if (status) filter.status = status;

    const alerts = await Alert.find(filter).sort({ createdAt: -1 }).limit(Number(limit));

    if (!alerts.length) {
      return res.status(404).json({ success: false, message: 'No alerts found for this user' });
    }

    return res.status(200).json({ success: true, count: alerts.length, alerts });
  } catch (err) {
    console.log('Error fetching user alerts:', err.message);
    return res.status(500).json({ success: false, message: 'Server error' });
  }
});

module.exports = router;
