const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const { connectDB } = require('./config/db');
const scanRoutes = require('./routes/scanRoutes');

const app = express();
const PORT = process.env.PORT || 5000;

// Connect to MongoDB Database
connectDB();

// CORS configuration (allow frontend origin)
app.use(cors({
  origin: ['http://localhost:5173', 'http://127.0.0.1:5173'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static uploaded images
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Health Check Endpoint
app.get('/api/health', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'FreshGuard API is running',
  });
});

// API Routes
app.use('/api/scans', scanRoutes);

// Multer & Global JSON Error Handler
app.use((err, req, res, next) => {
  if (err.name === 'MulterError') {
    return res.status(400).json({
      success: false,
      message: err.message || 'Please upload a valid image file',
    });
  }
  if (err) {
    return res.status(400).json({
      success: false,
      message: err.message || 'An error occurred during processing',
    });
  }
  next();
});

// Server Listener
app.listen(PORT, () => {
  console.log(`[FreshGuard API] Server running on http://localhost:${PORT}`);
});
