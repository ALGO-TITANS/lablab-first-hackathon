'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  ShieldCheck, 
  BarChart3, 
  UploadCloud, 
  History, 
  Settings, 
  Sparkles,
  TerminalSquare
} from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { href: '/upload', label: 'Upload CSV', icon: UploadCloud },
    { href: '/history', label: 'Execution History', icon: History },
    { href: '/settings', label: 'AI Settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-cyan-950/60 bg-[#070d1e]/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all duration-300">
            <div className="h-full w-full bg-[#0a0f24] rounded-[10px] flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">Safe CSV Analyst</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-500/30 text-cyan-400 font-semibold">
                Self-Healing AI
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Sandboxed Execution Worker
            </p>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href || (link.href !== '/' && pathname.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-950/70 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Quick Launch CTA */}
        <div className="flex items-center gap-3">
          <Link
            href="/upload"
            className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 shadow-md shadow-cyan-500/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Analyze Dataset</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
