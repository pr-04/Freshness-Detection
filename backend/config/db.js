const mongoose = require('mongoose');

let isConnected = false;

const connectDB = async () => {
  try {
    const connString = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/freshguard_ai';
    const conn = await mongoose.connect(connString, {
      serverSelectionTimeoutMS: 5000,
    });
    isConnected = true;
    console.log(`[Database] MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    isConnected = false;
    console.warn(`[Database Warning] Could not connect to MongoDB (${error.message}). Running with local memory fallback.`);
  }
};

const getIsConnected = () => isConnected;

module.exports = { connectDB, getIsConnected };
