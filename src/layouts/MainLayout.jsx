import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { Leaf } from 'lucide-react';
import Navbar from '../components/Navbar';

export default function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-[#fafaf8] font-sans text-stone-900 antialiased">
      <Navbar />
      <div className="flex-1"><Outlet /></div>
      <footer className="border-t border-stone-200 bg-white py-8 sm:py-10">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-5 px-4 text-center sm:flex-row sm:px-6 sm:text-left lg:px-8">
          <Link to="/" className="inline-flex items-center gap-2 text-sm font-bold text-stone-900"><span className="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-50 text-emerald-800"><Leaf className="h-4 w-4" /></span>FreshGuard AI</Link>
          <nav aria-label="Footer navigation" className="flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm font-medium text-stone-600">
            <Link to="/" className="hover:text-emerald-800">Home</Link>
            <Link to="/how-it-works" className="hover:text-emerald-800">How It Works</Link>
            <Link to="/history" className="hover:text-emerald-800">History</Link>
          </nav>
          <p className="max-w-xs text-xs leading-5 text-stone-500">Visual estimates only. Not a food-safety assessment.</p>
        </div>
      </footer>
    </div>
  );
}
