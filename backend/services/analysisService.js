const fs = require('node:fs/promises');

const DEFAULT_ML_SERVICE_URL = 'http://127.0.0.1:8000';
const DEFAULT_TIMEOUT_MS = 120000;
const SUPPORTED_FRUITS = new Map([
  ['apple', 'Apple'],
  ['banana', 'Banana'],
  ['guava', 'Guava'],
  ['orange', 'Orange'],
  ['pomegranate', 'Pomegranate'],
  ['strawberry', 'Strawberry'],
]);

class MlServiceError extends Error {
  constructor(message, statusCode, code) {
    super(message);
    this.name = 'MlServiceError';
    this.statusCode = statusCode;
    this.code = code;
  }
}

const getMlServiceUrl = () =>
  (process.env.ML_SERVICE_URL || DEFAULT_ML_SERVICE_URL).replace(/\/+$/, '');

const getTimeoutMs = () => {
  const timeout = Number.parseInt(process.env.ML_SERVICE_TIMEOUT_MS || DEFAULT_TIMEOUT_MS, 10);
  return Number.isFinite(timeout) && timeout > 0 ? timeout : DEFAULT_TIMEOUT_MS;
};

const canonicalFruit = (fruit) =>
  typeof fruit === 'string' ? SUPPORTED_FRUITS.get(fruit.trim().toLowerCase()) || null : null;

/** Forward the uploaded image and user-selected fruit to FastAPI. */
const analyzeImage = async (file, fruit) => {
  if (!file?.path) {
    throw new MlServiceError('The uploaded image is unavailable to the analysis service.', 400, 'IMAGE_UNAVAILABLE');
  }
  const selectedFruit = canonicalFruit(fruit);
  if (!selectedFruit) {
    throw new MlServiceError('Please select one of the supported fruits.', 400, 'UNSUPPORTED_FRUIT');
  }

  let imageBytes;
  try {
    imageBytes = await fs.readFile(file.path);
  } catch (error) {
    throw new MlServiceError(`Could not read the uploaded image: ${error.message}`, 500, 'IMAGE_READ_FAILED');
  }

  const formData = new FormData();
  formData.append('file', new Blob([imageBytes], { type: file.mimetype }), file.originalname);
  formData.append('fruit', selectedFruit);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), getTimeoutMs());

  let response;
  try {
    response = await fetch(`${getMlServiceUrl()}/predict`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new MlServiceError('The ML inference service timed out. Please try again.', 504, 'ML_SERVICE_TIMEOUT');
    }
    throw new MlServiceError(
      'The ML inference service is unavailable. Make sure FastAPI is running and ML_SERVICE_URL is correct.',
      503,
      'ML_SERVICE_UNAVAILABLE',
    );
  } finally {
    clearTimeout(timeout);
  }

  let prediction;
  try {
    prediction = await response.json();
  } catch {
    throw new MlServiceError('The ML inference service returned an invalid response.', 502, 'ML_INVALID_RESPONSE');
  }

  if (!response.ok) {
    const upstreamStatus = response.status;
    const statusCode = [400, 413, 503].includes(upstreamStatus) ? upstreamStatus : 502;
    const detail = prediction.detail || prediction.message || `HTTP ${upstreamStatus}`;
    throw new MlServiceError(`ML inference failed: ${detail}`, statusCode, 'ML_PREDICTION_FAILED');
  }

  const result = prediction.prediction;
  const probabilities = result?.probabilities;
  const validProbabilities = probabilities
    && Number.isFinite(probabilities.fresh)
    && Number.isFinite(probabilities.rotten)
    && probabilities.fresh >= 0 && probabilities.fresh <= 1
    && probabilities.rotten >= 0 && probabilities.rotten <= 1
    && Math.abs(probabilities.fresh + probabilities.rotten - 1) <= 0.001;
  const validFreshness = result?.uncertain === true
    ? result.freshness === 'Uncertain'
    : ['Fresh', 'Rotten'].includes(result?.freshness);
  if (prediction.success !== true || prediction.mock !== false
      || result?.fruit !== selectedFruit || result?.model !== 'MobileNetV2'
      || typeof result?.uncertain !== 'boolean' || !validFreshness || !validProbabilities) {
    throw new MlServiceError('The ML inference service response did not match the real prediction contract.', 502, 'ML_INVALID_RESPONSE');
  }

  return prediction;
};

module.exports = { analyzeImage, MlServiceError, canonicalFruit, SUPPORTED_FRUITS };
