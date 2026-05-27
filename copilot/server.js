const express = require('express');
const cors = require('cors');
require('dotenv').config();

const logger = require('./middleware/logger');

const app = express();
const PORT = process.env.PORT || 3000;

// Basic middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(logger);

// Import routes
const apiRoutes = require('./routes');

// Use routes
app.use('/api', apiRoutes);

// Basic route
app.get('/', (req, res) => {
    res.json({ 
        message: 'Express.js Backend API is running!',
        version: '1.0.0',
        timestamp: new Date().toISOString()
    });
});

// Health check route
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'OK', uptime: process.uptime() });
});

// Error handling middleware (must be last)
const { notFound, errorHandler } = require('./middleware/errorHandler');
app.use(notFound);
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Server is running on port ${PORT}`);
    console.log(`📋 API available at: http://localhost:${PORT}`);
});

module.exports = app;
