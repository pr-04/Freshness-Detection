export const SUPPORTED_FRUITS = [
  'Apple', 'Banana', 'Guava', 'Orange', 'Pomegranate', 'Strawberry',
];

export function canSubmitScan(file, fruit, isAnalyzing = false) {
  return Boolean(file && SUPPORTED_FRUITS.includes(fruit) && !isAnalyzing);
}

/** Present direct MobileNetV2 results without implying fruit recognition. */
export function getFreshnessPresentation(prediction = {}) {
  const fruit = prediction.fruit || prediction.produce || 'Selected fruit';
  const status = String(prediction.freshness || prediction.status || '').toLowerCase();
  const uncertain = Boolean(prediction.uncertain) || status === 'uncertain';
  const freshnessLabel = uncertain
    ? 'Uncertain'
    : status === 'fresh' ? 'Fresh' : status === 'rotten' ? 'Rotten' : null;
  const probabilities = prediction.probabilities || {
    fresh: prediction.freshProbability,
    rotten: prediction.rottenProbability,
  };
  return {
    fruit,
    freshnessLabel,
    uncertain,
    uncertaintyMessage: prediction.uncertainty_reason || prediction.uncertaintyReason
      || 'This image could not be checked confidently. Try a clearer photo.',
    freshProbability: probabilities.fresh,
    rottenProbability: probabilities.rotten,
  };
}

/** Present a direct classification scan or a basic older scan record. */
export function getScanHistorySummary(scan = {}) {
  const isDirectResult = scan.modelName === 'MobileNetV2'
    || (scan.freshProbability != null && scan.rottenProbability != null);
  if (isDirectResult || (scan.produce && scan.status)) {
    const status = String(scan.status || '').toLowerCase();
    return {
      title: scan.produce || 'Selected fruit',
      detail: status === 'uncertain'
        ? 'Freshness result uncertain'
        : status === 'fresh' || status === 'rotten'
          ? `${scan.produce || 'Fruit'}: ${status}`
          : 'Freshness result unavailable',
    };
  }

  return { title: scan.produce || 'Previous scan', detail: 'Freshness result unavailable' };
}

/** Return the Fresh/Rotten/Uncertain filter for one classification result. */
export function getHistoryStatus(scan = {}) {
  const status = String(scan.status || '').toLowerCase();
  const isDirectResult = scan.modelName === 'MobileNetV2'
    || (scan.freshProbability != null && scan.rottenProbability != null);

  if (isDirectResult) {
    if (scan.uncertain || status === 'uncertain') return 'uncertain';
    return ['fresh', 'rotten'].includes(status) ? status : 'other';
  }

  if (scan.uncertain || status === 'uncertain') return 'uncertain';
  return ['fresh', 'rotten'].includes(status) ? status : 'other';
}

export function getHistoryCounts(scans = []) {
  return scans.reduce((counts, scan) => {
    const status = getHistoryStatus(scan);
    counts.total += 1;
    if (status === 'fresh' || status === 'rotten' || status === 'uncertain') counts[status] += 1;
    return counts;
  }, { total: 0, fresh: 0, rotten: 0, uncertain: 0 });
}

