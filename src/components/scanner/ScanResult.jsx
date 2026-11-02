import React from 'react';
import { RefreshCw } from 'lucide-react';
import { getFreshnessPresentation } from './scanResultPresentation.js';

const displayScore = (value) => value != null && Number.isFinite(Number(value))
  ? Number(value).toFixed(3)
  : 'Unavailable';

export default function ScanResult({ resultData, onReset }) {
  const prediction = resultData?.prediction || resultData || {};
  const presentation = getFreshnessPresentation(prediction);
  const isFresh = presentation.freshnessLabel === 'Fresh';
  const isRotten = presentation.freshnessLabel === 'Rotten';

  return (
    <section className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm sm:p-7">
      <div>
        <p className="text-sm font-semibold text-emerald-800">Your result</p>
        <h3 className="mt-1 text-2xl font-bold text-stone-950">{presentation.fruit}</h3>
      </div>

      <article>
        {presentation.uncertain ? (
          <div role="status" className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-4 text-amber-950">
            <strong className="text-lg">Uncertain</strong>
            <p className="mt-1 text-sm">{presentation.uncertaintyMessage}</p>
          </div>
        ) : (
          <div className={`mt-4 rounded-2xl px-4 py-4 text-xl font-bold ${isFresh ? 'bg-emerald-50 text-emerald-950' : isRotten ? 'bg-rose-50 text-rose-950' : 'bg-stone-100 text-stone-800'}`}>
            {presentation.freshnessLabel || 'Result unavailable'}
          </div>
        )}

        {(presentation.freshProbability != null || presentation.rottenProbability != null) && <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-xl bg-stone-50 p-3">
            <p className="text-xs text-stone-500">Fresh class score</p>
            <p className="mt-1 font-semibold text-stone-900">{displayScore(presentation.freshProbability)}</p>
          </div>
          <div className="rounded-xl bg-stone-50 p-3">
            <p className="text-xs text-stone-500">Rotten class score</p>
            <p className="mt-1 font-semibold text-stone-900">{displayScore(presentation.rottenProbability)}</p>
          </div>
        </div>}
        <p className="mt-3 text-xs text-stone-500">Visual estimate only — not a food-safety assessment.</p>
      </article>

      <button type="button" onClick={onReset} className="mt-5 inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-emerald-800 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-900 focus:outline-none focus:ring-4 focus:ring-emerald-800/20">
        <RefreshCw className="h-4 w-4" />Scan another fruit
      </button>
    </section>
  );
}
