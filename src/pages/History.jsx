import React, { useEffect, useMemo, useState } from 'react';
import { CalendarDays, ChevronDown, ChevronUp, Image, LoaderCircle, RefreshCw, Trash2 } from 'lucide-react';
import { getHistoryCounts, getHistoryStatus, getScanHistorySummary } from '../components/scanner/scanResultPresentation.js';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const FILTERS = ['All', 'Fresh', 'Rotten', 'Uncertain'];

const statusStyles = {
  fresh: 'bg-emerald-100 text-emerald-900',
  rotten: 'bg-rose-100 text-rose-900',
  uncertain: 'bg-amber-100 text-amber-950',
  other: 'bg-stone-100 text-stone-600',
};

const formatDate = (value) => {
  if (!value) return 'Date unavailable';
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? 'Date unavailable' : date.toLocaleString();
};

const formatScore = (value) => value != null && Number.isFinite(Number(value))
  ? Number(value).toFixed(3)
  : 'Unavailable';

export default function History() {
  const [scans, setScans] = useState([]);
  const [filter, setFilter] = useState('All');
  const [expandedId, setExpandedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  const loadHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_URL}/api/scans`);
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.message || 'Could not load scan history.');
      setScans(Array.isArray(data.scans) ? data.scans : []);
    } catch (loadError) {
      setError(loadError.name === 'TypeError'
        ? 'Could not load your scan history. Check your connection and try again.'
        : loadError.message || 'Could not load your scan history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadHistory(); }, []);

  const counts = useMemo(() => getHistoryCounts(scans), [scans]);
  const filteredScans = useMemo(() => filter === 'All'
    ? scans
    : scans.filter((scan) => getHistoryStatus(scan) === filter.toLowerCase()), [scans, filter]);

  const handleDelete = async (scan) => {
    if (!window.confirm(`Delete the ${scan.produce || 'fruit'} scan from history?`)) return;
    setDeletingId(scan.id);
    setError('');
    try {
      const response = await fetch(`${API_URL}/api/scans/${encodeURIComponent(scan.id)}`, { method: 'DELETE' });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.message || 'Could not delete this scan.');
      setScans((current) => current.filter((item) => item.id !== scan.id));
      if (expandedId === scan.id) setExpandedId(null);
    } catch (deleteError) {
      setError(deleteError.message || 'Could not delete this scan.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <main className="mx-auto min-h-[65vh] max-w-6xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-emerald-800">Your recent checks</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-stone-950 sm:text-4xl">Scan history</h1>
        </div>
        <button type="button" onClick={loadHistory} disabled={loading} className="inline-flex min-h-10 items-center gap-2 rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-50 disabled:opacity-50">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </header>

      {error && <p role="alert" className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900">{error}</p>}

      <section aria-label="Scan totals" className="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          ['Total scans', counts.total, 'text-stone-950'],
          ['Fresh', counts.fresh, 'text-emerald-800'],
          ['Rotten', counts.rotten, 'text-rose-800'],
          ['Uncertain', counts.uncertain, 'text-amber-800'],
        ].map(([label, value, color]) => (
          <div key={label} className="rounded-2xl border border-stone-200 bg-white px-4 py-4 shadow-sm sm:px-5">
            <p className="text-xs font-medium text-stone-500 sm:text-sm">{label}</p>
            <p className={`mt-1 text-2xl font-bold ${color}`}>{loading || (error && scans.length === 0) ? '—' : value}</p>
          </div>
        ))}
      </section>

      <section className="mt-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-bold text-stone-900">Previous scans</h2>
          <div className="flex rounded-xl bg-stone-100 p-1" aria-label="Filter scans">
            {FILTERS.map((item) => (
              <button key={item} type="button" onClick={() => setFilter(item)} aria-pressed={filter === item}
                className={`rounded-lg px-3 py-2 text-xs font-semibold transition sm:px-4 ${filter === item ? 'bg-white text-emerald-900 shadow-sm' : 'text-stone-600 hover:text-stone-900'}`}>
                {item}
              </button>
            ))}
          </div>
        </div>
        <p className="mt-2 text-xs text-stone-500">Showing up to the latest 50 scans.</p>

        {loading ? (
          <div className="mt-5 flex items-center justify-center gap-2 rounded-2xl border border-stone-200 bg-white py-14 text-sm text-stone-600"><LoaderCircle className="h-4 w-4 animate-spin" /> Loading your scans…</div>
        ) : error && scans.length === 0 ? (
          <div role="status" className="mt-5 rounded-2xl border border-stone-200 bg-white px-6 py-12 text-center text-sm text-stone-600">Scan history is unavailable right now. Use Refresh to try again.</div>
        ) : scans.length === 0 ? (
          <div className="mt-5 rounded-2xl border border-dashed border-stone-300 bg-white px-6 py-14 text-center">
            <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-emerald-800"><Image className="h-5 w-5" /></span>
            <h3 className="mt-4 text-base font-semibold text-stone-900">No scans yet</h3>
            <p className="mt-1 text-sm text-stone-600">Your fruit checks will appear here.</p>
          </div>
        ) : filteredScans.length === 0 ? (
          <p className="mt-5 rounded-2xl border border-stone-200 bg-white px-5 py-10 text-center text-sm text-stone-600">No {filter.toLowerCase()} scans in your history.</p>
        ) : (
          <ul className="mt-4 divide-y divide-stone-100 overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm">
            {filteredScans.map((scan) => {
              const status = getHistoryStatus(scan);
              const summary = getScanHistorySummary(scan);
              const expanded = expandedId === scan.id;
              const imageUrl = scan.imagePath ? `${API_URL}${scan.imagePath}` : null;
              const detailsId = `scan-detail-${scan.id}`;
              return (
                <li key={scan.id} className="p-4 sm:p-5">
                  <div className="flex flex-wrap items-center gap-3">
                    {imageUrl ? <img src={imageUrl} alt="" className="h-14 w-14 rounded-xl bg-stone-100 object-cover" /> : <span className="flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-50 text-2xl" aria-hidden="true">🍃</span>}
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-semibold text-stone-900">{summary.title}</p>
                      <p className="mt-0.5 text-sm text-stone-600">{summary.detail}</p>
                      <p className="mt-1 inline-flex items-center gap-1 text-xs text-stone-500"><CalendarDays className="h-3.5 w-3.5" />{formatDate(scan.createdAt)}</p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${statusStyles[status] || statusStyles.other}`}>{status === 'other' ? 'Result unavailable' : status}</span>
                    <button type="button" aria-expanded={expanded} aria-controls={detailsId} onClick={() => setExpandedId(expanded ? null : scan.id)} className="inline-flex min-h-9 items-center gap-1 rounded-lg px-2 text-sm font-semibold text-emerald-900 hover:bg-emerald-50">
                      {expanded ? 'Hide details' : 'View details'} {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                    <button type="button" onClick={() => handleDelete(scan)} disabled={deletingId === scan.id} aria-label={`Delete ${summary.title} scan`} className="inline-flex min-h-9 min-w-9 items-center justify-center rounded-lg text-stone-500 hover:bg-rose-50 hover:text-rose-800 disabled:opacity-50">
                      {deletingId === scan.id ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                    </button>
                  </div>

                  {expanded && <div id={detailsId} className="ml-0 mt-4 grid gap-3 rounded-xl bg-stone-50 p-4 text-sm sm:ml-[4.25rem] sm:grid-cols-2">
                    <p><span className="text-stone-500">Fruit:</span> <span className="font-medium text-stone-900">{scan.produce || summary.title}</span></p>
                    <p><span className="text-stone-500">Result:</span> <span className="font-medium capitalize text-stone-900">{status}</span></p>
                    {scan.freshProbability != null && <p><span className="text-stone-500">Fresh class score:</span> <span className="font-medium text-stone-900">{formatScore(scan.freshProbability)}</span></p>}
                    {scan.rottenProbability != null && <p><span className="text-stone-500">Rotten class score:</span> <span className="font-medium text-stone-900">{formatScore(scan.rottenProbability)}</span></p>}
                    {scan.uncertaintyReason && <p className="sm:col-span-2"><span className="text-stone-500">Why uncertain:</span> <span className="text-stone-800">{scan.uncertaintyReason}</span></p>}
                    {scan.freshProbability == null && scan.rottenProbability == null && !scan.uncertaintyReason && <p className="text-stone-500 sm:col-span-2">Detailed scores are not available for this older scan.</p>}
                  </div>}
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </main>
  );
}
