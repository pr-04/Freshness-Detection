import React from 'react';
import { Link } from 'react-router-dom';
import { Leaf, Scan } from 'lucide-react';

export default function Logo({ className = '' }) {
  return (
    <Link to="/" className={`inline-flex items-center gap-2.5 group focus:outline-none ${className}`}>
      {/* Icon Badge */}
      <div className="relative flex items-center justify-center w-9 h-9 rounded-xl bg-emerald-600/10 text-emerald-600 border border-emerald-600/20 group-hover:bg-emerald-600 group-hover:text-white transition-all duration-200">
        <Leaf className="w-5 h-5 transition-transform duration-200 group-hover:scale-105" />
        <Scan className="w-3 h-3 absolute -bottom-0.5 -right-0.5 text-emerald-700 group-hover:text-emerald-100" />
      </div>

      {/* Text Branding */}
      <div className="flex items-center gap-1.5">
        <span className="text-lg font-bold tracking-tight text-neutral-900 font-sans">
          Fresh<span className="text-emerald-700 font-extrabold">Guard</span>
        </span>
        <span className="text-[10px] font-bold tracking-wider px-1.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 uppercase border border-emerald-200/60">
          AI
        </span>
      </div>
    </Link>
  );
}
