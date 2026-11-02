import React from 'react';
import { ArrowRight, Camera, CheckCircle2, CircleHelp, Leaf } from 'lucide-react';
import { Link } from 'react-router-dom';

const steps = [
  { number: '01', title: 'Select your fruit', description: 'Choose the fruit you want to check.', icon: Leaf },
  { number: '02', title: 'Upload a photo', description: 'Upload or capture a clear image of one fruit.', icon: Camera },
  { number: '03', title: 'Check freshness', description: 'View your freshness result in seconds.', icon: CheckCircle2 },
];

export default function HowItWorks() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8">
      <header className="mx-auto max-w-2xl text-center">
        <p className="text-sm font-semibold text-emerald-800">Simple by design</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-stone-950 sm:text-5xl">How it works</h1>
        <p className="mt-4 text-base leading-7 text-stone-600">A quick visual check, from your photo to a clear result.</p>
      </header>

      <ol className="mt-10 grid gap-4 md:grid-cols-3 md:gap-5">
        {steps.map(({ number, title, description, icon: Icon }) => (
          <li key={number} className="rounded-3xl border border-stone-200 bg-white p-6 shadow-sm sm:p-7">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-emerald-800">{number}</span>
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-800"><Icon className="h-5 w-5" /></span>
            </div>
            <h2 className="mt-7 text-xl font-bold text-stone-950">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-stone-600">{description}</p>
          </li>
        ))}
      </ol>

      <section className="mt-10 rounded-3xl bg-[#edf4e9] p-6 sm:p-8">
        <div className="flex items-center gap-2"><CircleHelp className="h-5 w-5 text-emerald-800" /><h2 className="text-lg font-bold text-stone-950">Understanding your result</h2></div>
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          {[
            ['Fresh', 'Visually classified as Fresh.', 'bg-emerald-100 text-emerald-950'],
            ['Rotten', 'Visually classified as Rotten.', 'bg-rose-100 text-rose-950'],
            ['Uncertain', 'The prediction is not sufficiently confident.', 'bg-amber-100 text-amber-950'],
          ].map(([label, description, style]) => (
            <div key={label} className="rounded-2xl bg-white p-4">
              <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${style}`}>{label}</span>
              <p className="mt-3 text-sm leading-6 text-stone-700">{description}</p>
            </div>
          ))}
        </div>
        <p className="mt-5 text-xs leading-5 text-stone-600">Results are AI-based visual estimates and should not be used to determine food safety or edibility.</p>
      </section>

      <div className="mt-8 text-center">
        <Link to="/#scanner" className="inline-flex items-center gap-2 rounded-xl bg-emerald-800 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-900">Check your fruit <ArrowRight className="h-4 w-4" /></Link>
      </div>
    </main>
  );
}
