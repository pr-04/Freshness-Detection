const test = require('node:test');
const assert = require('node:assert/strict');
const Module = require('node:module');
const path = require('node:path');

let isConnected = true;
let saveError = null;
let savedDocuments = [];

class FakeScan {
  constructor(data) {
    Object.assign(this, data);
    this._id = { toString: () => `db_${savedDocuments.length + 1}` };
  }

  async save() {
    if (saveError) throw saveError;
    savedDocuments.push(this);
    return this;
  }
}

const substitutions = new Map([
  [require.resolve('../models/Scan'), FakeScan],
  [require.resolve('../config/db'), { getIsConnected: () => isConnected }],
  [require.resolve('../services/analysisService'), {
    analyzeImage: async (_file, fruit) => ({
      success: true,
      mock: false,
      prediction: {
        fruit: ({ apple: 'Apple', banana: 'Banana', guava: 'Guava', orange: 'Orange', pomegranate: 'Pomegranate', strawberry: 'Strawberry' })[String(fruit || '').trim().toLowerCase()],
        freshness: 'Fresh', uncertain: false, uncertainty_reason: null,
        probabilities: { fresh: 0.93, rotten: 0.07 }, model: 'MobileNetV2',
      },
    }),
    canonicalFruit: (fruit) => ({ apple: 'Apple', banana: 'Banana', guava: 'Guava', orange: 'Orange', pomegranate: 'Pomegranate', strawberry: 'Strawberry' })[String(fruit || '').trim().toLowerCase()] || null,
  }],
]);
const originals = new Map();
for (const [filename, exportsValue] of substitutions) {
  const cached = require.cache[filename];
  originals.set(filename, cached || null);
  const replacement = cached || new Module(filename, module);
  replacement.filename = filename;
  replacement.loaded = true;
  replacement.exports = exportsValue;
  require.cache[filename] = replacement;
}
const controllerPath = require.resolve('../controllers/scanController');
delete require.cache[controllerPath];
const { createScan, getScans } = require('../controllers/scanController');

function responseRecorder() {
  return {
    statusCode: 200,
    status(code) { this.statusCode = code; return this; },
    json(body) { this.body = body; return this; },
  };
}

function scanRequest(fruit = 'Apple') {
  return {
    body: { fruit },
    file: { path: path.join('uploads', 'img.jpg'), filename: 'image-123.jpg', originalname: 'fruit.jpg' },
  };
}

test('connected persistence branch stores direct classification metadata', async () => {
  isConnected = true;
  saveError = null;
  const response = responseRecorder();
  await createScan(scanRequest(), response);
  assert.equal(response.statusCode, 201);
  assert.equal(response.body.scan.produce, 'Apple');
  assert.equal(response.body.scan.status, 'fresh');
  assert.equal(response.body.scan.freshProbability, 0.93);
  assert.equal(response.body.scan.rottenProbability, 0.07);
  assert.equal(response.body.scan.modelName, 'MobileNetV2');
  assert.equal(response.body.scan.imagePath, '/uploads/image-123.jpg');
  assert.equal('detections' in response.body.scan, false);
  assert.equal('bbox' in response.body.scan, false);
});

test('MongoDB save errors retain the in-memory fallback', async () => {
  isConnected = true;
  saveError = new Error('simulated database save failure');
  const response = responseRecorder();
  await createScan(scanRequest('Banana'), response);
  assert.equal(response.statusCode, 201);
  assert.match(response.body.scan.id, /^mem_/);
  assert.equal(response.body.scan.produce, 'Banana');
  saveError = null;
});

test('offline database fallback returns the new scan in scan history', async () => {
  isConnected = false;
  const response = responseRecorder();
  await createScan(scanRequest(), response);
  assert.equal(response.statusCode, 201);
  const history = responseRecorder();
  await getScans({}, history);
  assert.equal(history.statusCode, 200);
  assert.ok(history.body.scans.some((scan) => scan.id === response.body.scan.id));
  isConnected = true;
});

test('missing or excluded fruit selection is rejected before inference', async () => {
  const response = responseRecorder();
  await createScan(scanRequest('Grape'), response);
  assert.equal(response.statusCode, 400);
  assert.equal(response.body.code, 'UNSUPPORTED_FRUIT');
});

test.after(() => {
  delete require.cache[controllerPath];
  for (const [filename, original] of originals) {
    if (original) require.cache[filename] = original;
    else delete require.cache[filename];
  }
});
