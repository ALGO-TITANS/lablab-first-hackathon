import React from 'react';
import Link from 'next/link';
import { 
  ShieldCheck, 
  Wrench, 
  Cpu, 
  BarChart3, 
  Lock, 
  Sparkles, 
  ArrowRight, 
  Terminal, 
  CheckCircle2,
  FileSpreadsheet
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="space-y-16 py-6 sm:py-12">
      {/* Hero Section */}
      <section className="relative text-center max-w-4xl mx-auto space-y-6">
        {/* Glow backdrop */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-cyan-500/10 blur-[120px] rounded-full -z-10 pointer-events-none" />

        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-medium shadow-sm shadow-cyan-500/20">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Lablab.ai Hackathon Submission · Team ALGOTITANS</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-[1.15]">
          Safe CSV Analyst & <br />
          <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
            Self-Healing AI Agent
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Ask questions in plain English. Get real computations, not AI hallucinations. 
          If generated Python code crashes, our <span className="text-cyan-400 font-semibold">Self-Healing Diagnostic Agent</span> automatically pinpoints the bug, repairs the code, and recovers execution inside an AST-hardened sandbox.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <Link
            href="/upload"
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-sm shadow-lg shadow-cyan-500/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Sparkles className="w-4 h-4" />
            <span>Start Analyzing Data</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/40 text-slate-200 font-medium text-sm transition-all hover:bg-slate-850"
          >
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            <span>Open Dashboard</span>
          </Link>
        </div>
      </section>

      {/* Live Self-Healing Workflow Card */}
      <section className="rounded-2xl border border-cyan-500/30 bg-[#091026]/90 p-6 sm:p-8 backdrop-blur-xl shadow-2xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
          <div className="space-y-4 max-w-lg">
            <div className="inline-flex items-center gap-1.5 text-xs font-mono uppercase tracking-wider text-cyan-400 font-bold">
              <Wrench className="w-4 h-4" />
              The Core Differentiator
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              Autonomous Error Diagnosis & Self-Healing Execution Loop
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              When generated Pandas code encounters a mismatch (e.g. column casing, string dates, or type conflicts), traditional tools crash. CrisisLens/Safe CSV Analyst captures the traceback, asks the AI repair specialist to diagnose against the dataset schema, and re-executes cleanly without human intervention.
            </p>
            <div className="flex flex-wrap gap-2 text-xs font-mono">
              <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                Max 2 Retries
              </span>
              <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                8s Hard Timeout
              </span>
              <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
                Zero Credential Leakage
              </span>
            </div>
          </div>

          {/* Timeline Visual Illustration */}
          <div className="w-full lg:w-[460px] rounded-xl border border-slate-800 bg-[#050914] p-4 text-xs font-mono space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-slate-400">
              <span className="flex items-center gap-2">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                Execution Timeline
              </span>
              <span className="text-emerald-400">Restored</span>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                <span className="text-slate-300">1. Generating Python Code</span>
                <span className="text-emerald-400">✓ Done</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-rose-950/30 border border-rose-500/30">
                <span className="text-rose-300">2. Executing: Caught KeyError &apos;Region&apos;</span>
                <span className="text-rose-400">✕ Error</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-amber-950/30 border border-amber-500/30">
                <span className="text-amber-300">3. AI Repair: Schema Normalized to &apos;region&apos;</span>
                <span className="text-amber-400">⟳ Healed</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-emerald-950/30 border border-emerald-500/30">
                <span className="text-emerald-300">4. Verified Result: 5 Bar Segments</span>
                <span className="text-emerald-400">✓ Success</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Pillar Grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-xl bg-[#0a1128]/70 border border-slate-800 p-6 space-y-3 hover:border-cyan-500/30 transition-all">
          <div className="p-3 rounded-lg bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 w-fit">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-white">AST-Guarded Sandbox</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Strict Python Abstract Syntax Tree analysis stops malicious imports (os, sys, subprocess, requests, eval) before execution ever begins.
          </p>
        </div>

        <div className="rounded-xl bg-[#0a1128]/70 border border-slate-800 p-6 space-y-3 hover:border-blue-500/30 transition-all">
          <div className="p-3 rounded-lg bg-blue-950/60 border border-blue-500/30 text-blue-400 w-fit">
            <Lock className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-white">Zero Credential Exposure</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Code runs inside a detached subprocess with an empty environment dictionary. API keys and host variables are never accessible to executed code.
          </p>
        </div>

        <div className="rounded-xl bg-[#0a1128]/70 border border-slate-800 p-6 space-y-3 hover:border-indigo-500/30 transition-all">
          <div className="p-3 rounded-lg bg-indigo-950/60 border border-indigo-500/30 text-indigo-400 w-fit">
            <BarChart3 className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-white">Interactive Visualizations</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Automatic chart type selection based on query semantics. Dynamically renders Bar, Line, Area, and Pie charts with Recharts and CSV export.
          </p>
        </div>
      </section>
    </div>
  );
}
