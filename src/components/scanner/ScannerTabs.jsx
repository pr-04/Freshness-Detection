import React from 'react';
import { Camera, Upload } from 'lucide-react';

export default function ScannerTabs({ activeTab, onTabChange }) {
  return (
    <div className="inline-flex items-center p-1 rounded-xl bg-stone-100 border border-stone-200/80 w-full sm:w-auto font-sans">
      <button
        type="button"
        onClick={() => onTabChange('camera')}
        className={`flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-150 focus:outline-none ${
          activeTab === 'camera'
            ? 'bg-white text-emerald-800 shadow-2xs border border-stone-200/60'
            : 'text-stone-600 hover:text-stone-900'
        }`}
        aria-selected={activeTab === 'camera'}
        role="tab"
      >
        <Camera className="w-4 h-4" />
        <span>Camera</span>
      </button>

      <button
        type="button"
        onClick={() => onTabChange('upload')}
        className={`flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all duration-150 focus:outline-none ${
          activeTab === 'upload'
            ? 'bg-white text-emerald-800 shadow-2xs border border-stone-200/60'
            : 'text-stone-600 hover:text-stone-900'
        }`}
        aria-selected={activeTab === 'upload'}
        role="tab"
      >
        <Upload className="w-4 h-4" />
        <span>Upload</span>
      </button>
    </div>
  );
}
