import React from 'react';
import { Sparkles } from 'lucide-react';

export default function AnalysisLoader() {
  return (
    <div className="bg-white rounded-2xl border border-stone-200 p-6 sm:p-8 space-y-5 shadow-xs text-left" role="status" aria-live="polite">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <h3 className="text-base font-bold text-neutral-900 tracking-tight">Checking your fruit</h3>
          <p className="text-xs text-stone-500 font-normal">Your visual freshness estimate will be ready in a moment.</p>
        </div>
      </div>
      <div className="h-2 rounded-full bg-stone-100 overflow-hidden">
        <div className="h-full w-1/3 bg-emerald-600 rounded-full animate-pulse" />
      </div>
    </div>
  );
}
