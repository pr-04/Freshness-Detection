import React, { useEffect, useState } from 'react';
import { Camera, Check, ScanLine, Upload } from 'lucide-react';
import ScannerTabs from './ScannerTabs';
import CameraPreview from './CameraPreview';
import UploadArea from './UploadArea';
import AnalysisLoader from './AnalysisLoader';
import ScanResult from './ScanResult';
import { analyzeImage } from '../../services/analysisService';
import { canSubmitScan, SUPPORTED_FRUITS } from './scanResultPresentation.js';

export default function ScannerWorkflow() {
  const [inputMode, setInputMode] = useState('upload');
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFruit, setSelectedFruit] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
  }, [previewUrl]);

  const handleFileSelect = (file) => {
    if (!file) return;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError('');
  };

  const handleFileRemove = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError('');
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile || !SUPPORTED_FRUITS.includes(selectedFruit)) return;
    setIsAnalyzing(true);
    setResult(null);
    setError('');
    try {
      setResult(await analyzeImage(selectedFile, selectedFruit));
    } catch (analysisError) {
      setError(analysisError.message || 'Could not check this image. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setSelectedFruit('');
    setPreviewUrl(null);
    setIsAnalyzing(false);
    setResult(null);
    setError('');
    setInputMode('upload');
  };

  const canSubmit = canSubmitScan(selectedFile, selectedFruit, isAnalyzing);

  return (
    <section id="scanner" className="scroll-mt-24 rounded-[2rem] border border-stone-200 bg-white p-5 shadow-sm sm:p-8 lg:p-10">
      <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-emerald-700">A quick visual check</p>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">Check Your Fruit</h2>
        </div>
        <p className="max-w-sm text-sm leading-6 text-stone-600">Choose one fruit, then upload a photo or take one now.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(260px,0.85fr)] lg:items-start">
        <div className="space-y-4">
          <div>
            <label htmlFor="fruit-selection" className="mb-2 block text-sm font-semibold text-stone-800">Which fruit?</label>
            <select
              id="fruit-selection"
              name="fruit"
              required
              value={selectedFruit}
              onChange={(event) => { setSelectedFruit(event.target.value); setError(''); setResult(null); }}
              className="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-sm text-stone-900 outline-none transition focus:border-emerald-700 focus:ring-4 focus:ring-emerald-700/10"
            >
              <option value="">Select a fruit</option>
              {SUPPORTED_FRUITS.map((fruit) => <option key={fruit} value={fruit}>{fruit}</option>)}
            </select>
          </div>

          <div className="space-y-3">
            <ScannerTabs
              activeTab={inputMode}
              onTabChange={(tab) => { setInputMode(tab); setError(''); }}
            />
            {inputMode === 'camera' ? (
              <CameraPreview onUsePhoto={handleFileSelect} />
            ) : (
              <UploadArea
                selectedFile={selectedFile}
                previewUrl={previewUrl}
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                error=""
                setError={setError}
              />
            )}
          </div>

          {inputMode === 'camera' && error && <p role="alert" className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">{error}</p>}
          <button
            type="button"
            onClick={handleStartAnalysis}
            disabled={!canSubmit}
            className="inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-emerald-800 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-900 focus:outline-none focus:ring-4 focus:ring-emerald-800/20 disabled:cursor-not-allowed disabled:bg-stone-200 disabled:text-stone-500 sm:w-auto sm:min-w-56"
          >
            <ScanLine className="h-4 w-4" />
            Check freshness
          </button>
          {!canSubmit && !isAnalyzing && <p className="text-xs text-stone-500">Choose a fruit and add a JPG or PNG photo to continue.</p>}
        </div>

        <aside className="rounded-2xl bg-emerald-50/70 p-5 sm:p-6">
          <p className="text-sm font-semibold text-emerald-950">For a clearer result</p>
          <ul className="mt-4 space-y-3 text-sm leading-6 text-stone-700">
            <li className="flex gap-2"><Check className="mt-1 h-4 w-4 shrink-0 text-emerald-700" /> Show one fruit clearly</li>
            <li className="flex gap-2"><Check className="mt-1 h-4 w-4 shrink-0 text-emerald-700" /> Use even, natural light</li>
            <li className="flex gap-2"><Check className="mt-1 h-4 w-4 shrink-0 text-emerald-700" /> Keep the surface in focus</li>
          </ul>
          <div className="mt-6 flex items-center gap-2 border-t border-emerald-900/10 pt-4 text-xs text-stone-600">
            {inputMode === 'camera' ? <Camera className="h-4 w-4 text-emerald-800" /> : <Upload className="h-4 w-4 text-emerald-800" />}
            <span>JPG or PNG · up to 10 MB</span>
          </div>
        </aside>
      </div>

      {isAnalyzing && <div className="mt-7"><AnalysisLoader /></div>}
      {error && inputMode === 'upload' && <p role="alert" className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">{error}</p>}
      {result && <div className="mt-7"><ScanResult resultData={result} onReset={handleReset} /></div>}
    </section>
  );
}
