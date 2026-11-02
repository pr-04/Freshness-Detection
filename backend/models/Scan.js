const mongoose = require('mongoose');

const scanSchema = new mongoose.Schema({
  userId: {
    type: String,
    required: false,
  },
  imageName: {
    type: String,
    required: true,
  },
  produce: {
    type: String,
    default: null,
  },
  type: {
    type: String,
    default: null,
  },
  status: {
    type: String,
    default: null,
  },
  confidence: {
    type: Number,
    default: null,
  },
  freshness: {
    type: Number,
    default: null,
  },
  signs: {
    type: [String],
    default: [],
  },
  recommendation: {
    type: String,
    default: null,
  },
  models: {
    classifier: String,
  },
  task: String,
  mock: {
    type: Boolean,
    default: null,
  },
  // Direct MobileNetV2 classification fields.
  freshProbability: {
    type: Number,
    default: null,
  },
  rottenProbability: {
    type: Number,
    default: null,
  },
  modelName: {
    type: String,
    default: null,
  },
  uncertain: {
    type: Boolean,
    default: false,
  },
  uncertaintyReason: {
    type: String,
    default: null,
  },
  imagePath: {
    type: String,
    default: null,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model('Scan', scanSchema);
