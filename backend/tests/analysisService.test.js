const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { analyzeImage, MlServiceError } = require('../services/analysisService');

const validMlResponse = {
  success: true,
  mock: false,
  prediction: {
    fruit: 'Apple',
    freshness: 'Fresh',
    uncertain: false,
    uncertainty_reason: null,
    probabilities: { fresh: 0.93, rotten: 0.07 },
    model: 'MobileNetV2',
  },
};

async function createImageFixture(t) {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'freshguard-backend-'));
  const filePath = path.join(directory, 'fruit.png');
  await fs.writeFile(filePath, Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jv6sAAAAASUVORK5CYII=', 'base64'));
  t.after(() => fs.rm(directory, { recursive: true, force: true }));
  return { path: filePath, mimetype: 'image/png', originalname: 'fruit.png' };
}

function mockMlFetch(t, responseBody) {
  const previousFetch = global.fetch;
  let capturedRequest;
  global.fetch = async (url, options) => {
    capturedRequest = { url, options };
    return { ok: true, status: 200, json: async () => responseBody };
  };
  t.after(() => { global.fetch = previousFetch; });
  return () => capturedRequest;
}

function useMlServiceUrl(t, url) {
  const previousUrl = process.env.ML_SERVICE_URL;
  process.env.ML_SERVICE_URL = url;
  t.after(() => {
    if (previousUrl === undefined) delete process.env.ML_SERVICE_URL;
    else process.env.ML_SERVICE_URL = previousUrl;
  });
}

test('forwards the image and selected fruit and validates the direct prediction response', async (t) => {
  useMlServiceUrl(t, 'http://ml-service.test');
  const getRequest = mockMlFetch(t, validMlResponse);
  const file = await createImageFixture(t);
  const result = await analyzeImage(file, 'Apple');
  const request = getRequest();
  assert.equal(request.url, 'http://ml-service.test/predict');
  assert.equal(request.options.method, 'POST');
  assert.equal(request.options.body.get('fruit'), 'Apple');
  assert.equal(request.options.body.get('file').name, 'fruit.png');
  assert.deepEqual(result, validMlResponse);
});

test('rejects an invalid upstream prediction shape', async (t) => {
  useMlServiceUrl(t, 'http://ml-service.test');
  mockMlFetch(t, { success: true, mock: false });
  const file = await createImageFixture(t);
  await assert.rejects(
    analyzeImage(file, 'Apple'),
    (error) => error instanceof MlServiceError && error.code === 'ML_INVALID_RESPONSE',
  );
});

test('reports ML service unavailability with the existing service error contract', async (t) => {
  useMlServiceUrl(t, 'http://ml-service.test');
  const previousFetch = global.fetch;
  global.fetch = async () => { throw new Error('simulated connection failure'); };
  t.after(() => { global.fetch = previousFetch; });
  const file = await createImageFixture(t);
  await assert.rejects(
    analyzeImage(file, 'Apple'),
    (error) => error instanceof MlServiceError && error.statusCode === 503 && error.code === 'ML_SERVICE_UNAVAILABLE',
  );
});

test('rejects unsupported selected fruits before contacting FastAPI', async (t) => {
  const file = await createImageFixture(t);
  await assert.rejects(
    analyzeImage(file, 'Grape'),
    (error) => error instanceof MlServiceError && error.statusCode === 400 && error.code === 'UNSUPPORTED_FRUIT',
  );
});
