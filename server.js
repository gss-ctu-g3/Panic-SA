// server.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const mongoose = require('mongoose');
require('dotenv').config();
const jwt = require("jsonwebtoken");

const alertRoutes = require('./routes/alerts');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

// allow JSON requests
app.use(express.json());

// make io available in routes
app.set('io', io);

// use alert routes
app.use('/api', alertRoutes);

// socket.io connection
io.on('connection', (socket) => {
  console.log('Responder connected:', socket.id);
  socket.join('emergency-responders');

  socket.on('disconnect', () => {
    console.log('Responder disconnected:', socket.id);
  });
});

// connect to MongoDB
mongoose.connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => {
    console.log('Connected to MongoDB');
    const port = process.env.PORT || 3000;
    server.listen(port, () => {
      console.log('Server running on port', port);
    });
  })
  .catch((err) => {
    console.log('MongoDB connection error:', err.message);
    process.exit(1);
  });



