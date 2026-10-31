import React from 'react';
import { Wrench, AlertTriangle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { ExecutionAttempt } from '@/lib/types';

interface ErrorDiagnosisCardProps {
  failedAttempt: ExecutionAttempt;
  repairedAttempt: ExecutionAttempt;
}

export default function ErrorDiagnosisCard({
  failedAttempt,
  repairedAttempt,
}: ErrorDiagnosisCardProps) {
  return (
    <div className="rounded-xl border border-amber-500/30 bg-gradient-to-b from-amber-950/20 to-slate-900/40 p-5 backdrop-blur-md space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-amber-500/20">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-950 border border-amber-500/40 text-amber-400">
            <Wrench className="w-4 h-4 animate-spin-slow" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">Autonomous Self-Healing Diagnosis</h4>
            <p className="text-xs text-amber-300 font-mono">
              Runtime failure recovered on Attempt #{repairedAttempt.attempt_number}
            </p>
          </div>
        </div>
        <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-emerald-950 border border-emerald-500/40 text-emerald-300 flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Execution Restored
        </span>
      </div>

      {/* Probable Cause & Diagnosis */}
      <div className="rounded-lg bg-slate-950/70 border border-slate-800 p-3.5 space-y-1.5 text-xs">
        <span className="text-slate-400 uppercase tracking-wider font-semibold text-[10px]">
          Identified Root Cause:
        </span>
        <p className="text-slate-200 leading-relaxed font-sans">
          {repairedAttempt.diagnosis || failedAttempt.error_message || 'Detected runtime mismatch. Agent inspected dataset schema to normalize columns and types.'}
        </p>
        <div className="pt-1 flex items-center gap-2 text-rose-400 font-mono text-[11px]">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>Exception: [{failedAttempt.error_type}] {failedAttempt.error_message}</span>
        </div>
      </div>

      {/* Side-by-Side Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
        {/* Failed Attempt */}
        <div className="rounded-lg border border-rose-500/30 bg-rose-950/10 p-3 overflow-hidden">
          <div className="flex items-center justify-between text-rose-400 font-semibold mb-2 text-[11px]">
            <span>Initial Attempt #{failedAttempt.attempt_number} (Failed)</span>
            <span className="px-1.5 py-0.2 rounded bg-rose-950 text-rose-300 border border-rose-500/30">
              {failedAttempt.error_type}
            </span>
          </div>
          <pre className="text-slate-300 max-h-48 overflow-y-auto text-[11px] whitespace-pre">
            <code>{failedAttempt.code}</code>
          </pre>
        </div>

        {/* Repaired Attempt */}
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-950/10 p-3 overflow-hidden">
          <div className="flex items-center justify-between text-emerald-400 font-semibold mb-2 text-[11px]">
            <span>Repaired Attempt #{repairedAttempt.attempt_number} (Verified)</span>
            <span className="px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/30">
              Passed
            </span>
          </div>
          <pre className="text-slate-300 max-h-48 overflow-y-auto text-[11px] whitespace-pre">
            <code>{repairedAttempt.code}</code>
          </pre>
        </div>
      </div>
    </div>
  );
}
