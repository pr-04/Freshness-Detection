const Scan = require('../models/Scan');
const path = require('node:path');
const { analyzeImage, canonicalFruit } = require('../services/analysisService');
const { getIsConnected } = require('../config/db');

// In-memory fallback list if MongoDB is offline
const memoryScans = [];

// Format direct MobileNetV2 records without exposing legacy detector fields.
const formatScan = (doc) => ({
  id: doc._id ? doc._id.toString() : (doc.id || doc._id),
  imageName: doc.imageName || 'produce.jpg',
  produce: doc.produce,
  type: doc.type,
  status: doc.status,
  confidence: doc.confidence,
  freshness: doc.freshness,
  signs: doc.signs,
  recommendation: doc.recommendation,
  mock: doc.mock ?? null,
  freshProbability: doc.freshProbability ?? null,
  rottenProbability: doc.rottenProbability ?? null,
  modelName: doc.modelName || null,
  uncertain: doc.uncertain ?? false,
  uncertaintyReason: doc.uncertaintyReason || null,
  imagePath: doc.imagePath || null,
  createdAt: doc.createdAt,
});

/**
 * POST /api/scans
 * Upload an image, request real ML inference, and save the prediction metadata.
 */
const createScan = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'Please upload an image',
      });
    }

    const selectedFruit = canonicalFruit(req.body?.fruit);
    if (!selectedFruit) {
      return res.status(400).json({
        success: false,
        message: 'Please select Apple, Banana, Guava, Orange, Pomegranate, or Strawberry.',
        code: 'UNSUPPORTED_FRUIT',
      });
    }

    // Do not create a scan record unless the Python service returned real inference.
    const predictionResponse = await analyzeImage(req.file, selectedFruit);
    const prediction = predictionResponse.prediction;
    const uncertain = prediction.uncertain;
    const modelScore = Math.max(prediction.probabilities.fresh, prediction.probabilities.rotten);

    const scanData = {
      imageName: req.file.originalname,
      imagePath: req.file.filename ? `/uploads/${path.basename(req.file.filename)}` : null,
      produce: prediction.fruit,
      type: 'Fruit',
      status: prediction.freshness.toLowerCase(),
      confidence: uncertain ? null : modelScore,
      freshness: null,
      signs: [],
      recommendation: null,
      freshProbability: prediction.probabilities.fresh,
      rottenProbability: prediction.probabilities.rotten,
      modelName: prediction.model,
      uncertain,
      uncertaintyReason: prediction.uncertainty_reason || null,
      mock: false,
      createdAt: new Date(),
    };

    let savedResult = scanData;

    // Save to MongoDB if connected, or fallback to memory array
    if (getIsConnected()) {
      try {
        const scanDoc = new Scan(scanData);
        const savedDoc = await scanDoc.save();
        savedResult = formatScan(savedDoc);
      } catch (dbErr) {
        console.warn('[Database Warning] Scan persistence error:', dbErr.message);
        savedResult = { id: `mem_${Date.now()}`, ...scanData };
        memoryScans.unshift(savedResult);
      }
    } else {
      savedResult = { id: `mem_${Date.now()}`, ...scanData };
      memoryScans.unshift(savedResult);
    }

    return res.status(201).json({
      success: true,
      scan: savedResult,
      prediction: predictionResponse,
    });
  } catch (error) {
    console.error('[Scan Controller Error]', error);
    return res.status(error.statusCode || 500).json({
      success: false,
      message: error.message || 'Server error processing scan',
      ...(error.code ? { code: error.code } : {}),
    });
  }
};

/**
 * GET /api/scans
 * Get latest scans from MongoDB (limit 50, sorted by createdAt desc)
 */
const getScans = async (req, res) => {
  try {
    if (getIsConnected()) {
      const docs = await Scan.find().sort({ createdAt: -1 }).limit(50);
      const formattedScans = docs.map(formatScan);
      return res.status(200).json({
        success: true,
        scans: formattedScans,
      });
    }
    return res.status(200).json({
      success: true,
      scans: memoryScans.slice(0, 50),
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: 'Failed to retrieve scan records',
    });
  }
};

/**
 * GET /api/scans/:id
 * Get single scan details by ID
 */
const getScanById = async (req, res) => {
  try {
    const { id } = req.params;
    if (getIsConnected() && !id.startsWith('mem_')) {
      const doc = await Scan.findById(id);
      if (!doc) {
        return res.status(404).json({
          success: false,
          message: 'Scan not found',
        });
      }
      return res.status(200).json({
        success: true,
        scan: formatScan(doc),
      });
    }

    const memoryItem = memoryScans.find((s) => s.id === id);
    if (!memoryItem) {
      return res.status(404).json({
        success: false,
        message: 'Scan not found',
      });
    }
    return res.status(200).json({
      success: true,
      scan: memoryItem,
    });
  } catch (error) {
    return res.status(404).json({
      success: false,
      message: 'Scan not found',
    });
  }
};

/**
 * DELETE /api/scans/:id
 * Delete scan by ID
 */
const deleteScan = async (req, res) => {
  try {
    const { id } = req.params;
    if (getIsConnected() && !id.startsWith('mem_')) {
      const deleted = await Scan.findByIdAndDelete(id);
      if (!deleted) {
        return res.status(404).json({
          success: false,
          message: 'Scan not found',
        });
      }
    } else {
      const idx = memoryScans.findIndex((s) => s.id === id);
      if (idx !== -1) {
        memoryScans.splice(idx, 1);
      }
    }

    return res.status(200).json({
      success: true,
      message: 'Scan deleted successfully',
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: 'Failed to delete scan record',
    });
  }
};

module.exports = {
  createScan,
  getScans,
  getScanById,
  deleteScan,
};
