import React, { useEffect } from 'react';
import { ArrowDown, ArrowRight, Camera, ImagePlus, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import ScannerWorkflow from '../components/scanner/ScannerWorkflow';
import { SUPPORTED_FRUITS } from '../components/scanner/scanResultPresentation.js';

const fruitVisuals = {
  Apple: '🍎',
  Banana: '🍌',
  Guava: '🍈',
  Orange: '🍊',
  Pomegranate: '🍎',
  Strawberry: '🍓',
};

export default function Home() {
  useEffect(() => {
    if (window.location.hash === '#scanner') {
      requestAnimationFrame(() => document.getElementById('scanner')?.scrollIntoView());
    }
  }, []);

  return (
    <main className="pb-20">
      <section className="mx-auto grid max-w-7xl items-center gap-8 px-4 pb-10 pt-10 sm:px-6 sm:pb-14 sm:pt-14 lg:grid-cols-[1fr_0.9fr] lg:gap-12 lg:px-8 lg:pb-16">
        <div className="max-w-xl">
          <p className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-3 py-1.5 text-xs font-semibold text-emerald-900 shadow-sm">
            <Sparkles className="h-3.5 w-3.5" /> A simple visual freshness check
          </p>
          <h1 className="mt-5 text-4xl font-bold leading-tight tracking-tight text-stone-950 sm:text-5xl lg:text-6xl">Is Your Fruit <span className="text-emerald-800">Fresh?</span></h1>
          <p className="mt-4 max-w-lg text-base leading-7 text-stone-600 sm:text-lg">Check the visual freshness of your everyday fruits in seconds.</p>
          <a href="#scanner" className="mt-7 inline-flex min-h-12 items-center gap-2 rounded-xl bg-emerald-800 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-900 focus:outline-none focus:ring-4 focus:ring-emerald-800/20">
            Check your fruit <ArrowDown className="h-4 w-4" />
          </a>
        </div>

        <div aria-label="Fresh fruit illustration" className="relative mx-auto flex min-h-64 w-full max-w-lg items-center justify-center overflow-hidden rounded-[2rem] bg-[#eaf4e7] sm:min-h-80">
          <div className="absolute -right-12 -top-16 h-52 w-52 rounded-full bg-white/60" />
          <div className="absolute -bottom-20 -left-10 h-56 w-56 rounded-full bg-[#d8e9d3]" />
          <div className="relative flex items-end gap-1 sm:gap-3" aria-hidden="true">
            <span className="-rotate-12 text-6xl drop-shadow-sm sm:text-8xl">🍊</span>
            <span className="-translate-y-5 rotate-6 text-7xl drop-shadow-sm sm:text-9xl">🍎</span>
            <span className="translate-y-1 rotate-12 text-6xl drop-shadow-sm sm:text-8xl">🍌</span>
          </div>
          <div className="absolute bottom-5 left-5 inline-flex items-center gap-2 rounded-full bg-white/90 px-3 py-2 text-xs font-semibold text-stone-700 shadow-sm sm:bottom-7 sm:left-7">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-100 text-emerald-800"><Camera className="h-3.5 w-3.5" /></span>
            Upload or take a photo
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-7xl scroll-mt-24 px-4 sm:px-6 lg:px-8">
        <ScannerWorkflow />
      </div>

      <section className="mx-auto max-w-7xl px-4 pt-16 sm:px-6 sm:pt-20 lg:px-8">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-emerald-800">Six fruits to choose from</p>
            <h2 className="mt-1 text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">Made for your everyday fruit</h2>
          </div>
          <p className="max-w-sm text-sm leading-6 text-stone-600">Select the fruit in your photo before you start.</p>
        </div>
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-6">
          {SUPPORTED_FRUITS.map((fruit, index) => (
            <div key={fruit} className="flex min-h-28 items-center gap-3 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:flex-col sm:justify-center sm:gap-2 sm:text-center">
              <span className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full text-3xl ${index % 2 ? 'bg-amber-50' : 'bg-emerald-50'}`} aria-hidden="true">{fruitVisuals[fruit]}</span>
              <span className="text-sm font-semibold text-stone-800">{fruit}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto mt-16 max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] bg-stone-100 px-5 py-8 sm:px-10 sm:py-10">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-emerald-800">Three easy steps</p>
              <h2 className="mt-1 text-2xl font-bold tracking-tight text-stone-950">A little more confidence at a glance</h2>
            </div>
            <Link to="/how-it-works" className="inline-flex items-center gap-2 text-sm font-semibold text-emerald-900 hover:text-emerald-700">How it works <ArrowRight className="h-4 w-4" /></Link>
          </div>
          <div className="mt-7 grid gap-3 md:grid-cols-3">
            {[
              { number: '01', icon: '🍓', label: 'Select a fruit' },
              { number: '02', icon: <ImagePlus className="h-5 w-5" />, label: 'Upload or take a photo' },
              { number: '03', icon: '🌿', label: 'Check its freshness' },
            ].map((step) => (
              <div key={step.number} className="flex items-center gap-4 rounded-2xl bg-white p-4 sm:p-5">
                <span className="text-xs font-bold text-emerald-800">{step.number}</span>
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-xl text-emerald-800">{step.icon}</span>
                <span className="text-sm font-semibold text-stone-800">{step.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
