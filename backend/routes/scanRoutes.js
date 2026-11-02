const express = require('express');
const router = express.Router();
const upload = require('../middleware/upload');
const {
  createScan,
  getScans,
  getScanById,
  deleteScan,
} = require('../controllers/scanController');

// POST /api/scans - Upload produce image & process scan
router.post('/', upload.single('image'), createScan);

// GET /api/scans - Get latest scans
router.get('/', getScans);

// GET /api/scans/:id - Get single scan by ID
router.get('/:id', getScanById);

// DELETE /api/scans/:id - Delete scan record by ID
router.delete('/:id', deleteScan);

module.exports = router;
