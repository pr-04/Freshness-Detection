import React, { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import Logo from './Logo';

const links = [
  { label: 'Home', to: '/', end: true },
  { label: 'How It Works', to: '/how-it-works' },
  { label: 'History', to: '/history' },
];

const linkClass = ({ isActive }) => `rounded-lg px-3 py-2 text-sm font-semibold transition ${isActive ? 'bg-emerald-50 text-emerald-900' : 'text-stone-600 hover:bg-stone-50 hover:text-stone-950'}`;

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-stone-200/80 bg-[#fafaf8]/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Logo />
        <nav aria-label="Main navigation" className="hidden items-center gap-1 md:flex">
          {links.map((link) => <NavLink key={link.to} to={link.to} end={link.end} className={linkClass}>{link.label}</NavLink>)}
        </nav>
        <Link to="/#scanner" className="hidden rounded-xl bg-emerald-800 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-900 sm:inline-flex">Check your fruit</Link>
        <button type="button" onClick={() => setMenuOpen((open) => !open)} aria-expanded={menuOpen} aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'} className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-stone-700 hover:bg-stone-100 focus:outline-none focus:ring-2 focus:ring-emerald-700 md:hidden">
          {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>
      {menuOpen && <nav aria-label="Mobile navigation" className="border-t border-stone-200 bg-white px-4 py-3 md:hidden">
        <div className="mx-auto flex max-w-7xl flex-col gap-1">
          {links.map((link) => <NavLink key={link.to} to={link.to} end={link.end} onClick={() => setMenuOpen(false)} className={linkClass}>{link.label}</NavLink>)}
          <Link to="/#scanner" onClick={() => setMenuOpen(false)} className="mt-2 rounded-xl bg-emerald-800 px-4 py-3 text-center text-sm font-semibold text-white">Check your fruit</Link>
        </div>
      </nav>}
    </header>
  );
}
