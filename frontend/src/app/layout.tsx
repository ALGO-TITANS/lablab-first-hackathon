import type { Metadata } from 'next';
import { Suspense } from 'react';
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'Safe CSV Analyst | Self-Healing AI Execution Agent',
  description: 'Zero-Trust AI Data Science Platform with Automated Code Error Recovery and Sandboxed Execution',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col bg-[#070d1e] text-slate-100 antialiased selection:bg-cyan-500 selection:text-slate-950">
        <Suspense fallback={<div className="h-16 border-b border-slate-800 bg-[#070d1e]" />}>
          <Navbar />
        </Suspense>
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="border-t border-slate-900 bg-[#050914] py-6 text-center text-xs text-slate-500 font-mono">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p>Team ALGOTITANS — Lablab.ai Hackathon Submission</p>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5 text-cyan-400">
                <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
                AST-Sandbox Isolation
              </span>
              <span>FastAPI + Next.js</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
