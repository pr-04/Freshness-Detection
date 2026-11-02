const test = require('node:test');
const assert = require('node:assert/strict');
const Scan = require('../models/Scan');

test('schema accepts a direct MobileNetV2 scan', () => {
  const scan = new Scan({
    imageName: 'fruit.jpg', imagePath: '/uploads/fruit.jpg', produce: 'Apple', type: 'Fruit',
    status: 'fresh', freshProbability: 0.93, rottenProbability: 0.07,
    modelName: 'MobileNetV2', uncertain: false,
  });
  assert.equal(scan.validateSync(), undefined);
});

