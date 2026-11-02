import test from 'node:test';
import assert from 'node:assert/strict';
import {
  canSubmitScan,
  getFreshnessPresentation,
  getHistoryCounts,
  getHistoryStatus,
  getScanHistorySummary,
  SUPPORTED_FRUITS,
} from './scanResultPresentation.js';

test('fruit selection is required before a scan can be submitted', () => {
  assert.equal(canSubmitScan({ name: 'fruit.jpg' }, ''), false);
  assert.equal(canSubmitScan(null, 'Apple'), false);
  assert.equal(canSubmitScan({ name: 'fruit.jpg' }, 'Apple'), true);
  assert.equal(canSubmitScan({ name: 'fruit.jpg' }, 'Grape'), false);
  assert.equal(canSubmitScan({ name: 'fruit.jpg' }, 'Apple', true), false);
  assert.deepEqual(SUPPORTED_FRUITS, ['Apple', 'Banana', 'Guava', 'Orange', 'Pomegranate', 'Strawberry']);
});

test('direct Fresh and Rotten results show the selected category and both class scores', () => {
  const fresh = getFreshnessPresentation({
    fruit: 'Apple', freshness: 'Fresh', probabilities: { fresh: 0.91, rotten: 0.09 },
  });
  assert.equal(fresh.fruit, 'Apple');
  assert.equal(fresh.freshnessLabel, 'Fresh');
  assert.equal(fresh.freshProbability, 0.91);
  assert.equal(fresh.rottenProbability, 0.09);
  assert.equal(getFreshnessPresentation({ fruit: 'Orange', freshness: 'Rotten' }).freshnessLabel, 'Rotten');
});

test('uncertain direct result has no forced Fresh/Rotten class label', () => {
  const result = getFreshnessPresentation({
    fruit: 'Grape', freshness: 'Uncertain', uncertain: true,
    uncertainty_reason: 'The highest score is too low.',
  });
  assert.equal(result.freshnessLabel, 'Uncertain');
  assert.equal(result.uncertain, true);
  assert.match(result.uncertaintyMessage, /highest score/i);
});

test('dashboard summary supports direct and basic historical scan records', () => {
  assert.deepEqual(getScanHistorySummary({
    produce: 'Apple', status: 'fresh', modelName: 'MobileNetV2',
  }), { title: 'Apple', detail: 'Apple: fresh' });
  assert.deepEqual(getScanHistorySummary({ produce: 'Banana' }), {
    title: 'Banana', detail: 'Freshness result unavailable',
  });
});

test('history counts uncertain direct scans separately from Fresh and Rotten', () => {
  const scans = [
    { modelName: 'MobileNetV2', status: 'fresh' },
    { modelName: 'MobileNetV2', status: 'rotten' },
    { modelName: 'MobileNetV2', status: 'uncertain', uncertain: true },
  ];
  assert.deepEqual(getHistoryCounts(scans), { total: 3, fresh: 1, rotten: 1, uncertain: 1 });
});

