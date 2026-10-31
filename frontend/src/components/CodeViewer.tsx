'use client';

import React, { useState } from 'react';
import { Terminal, Copy, Check, Shield, AlertTriangle } from 'lucide-react';
import { ExecutionAttempt } from '@/lib/types';

interface CodeViewerProps {
  attempts: ExecutionAttempt[];
  finalCode: string;
}

export default function CodeViewer({ attempts, finalCode }: CodeViewerProps) {
  const [selectedAttemptIdx, setSelectedAttemptIdx] = useState<number>(
    attempts.length > 0 ? attempts.length - 1 : 0
  );
  const [copied, setCopied] = useState(false);

  const currentAttempt = attempts[selectedAttemptIdx];
  const displayCode = currentAttempt ? currentAttempt.code : finalCode;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(displayCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-[#070d1e] overflow-hidden shadow-xl">
      {/* Code Header */}
      <div className="p-3 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 bg-slate-900/60">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          </div>
          <span className="text-xs font-mono text-slate-300 font-semibold flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-cyan-400" />
            sandbox_executor.py
          </span>
        </div>

        {/* Attempt Switcher if multiple attempts exist */}
        <div className="flex items-center gap-2">
          {attempts.length > 1 && (
            <div className="flex items-center rounded-lg bg-slate-950 p-1 border border-slate-800">
              {attempts.map((att, idx) => (
                <button
                  key={att.attempt_number}
                  onClick={() => setSelectedAttemptIdx(idx)}
                  className={`text-[11px] px-2.5 py-1 rounded font-mono transition-all flex items-center gap-1.5 ${
                    selectedAttemptIdx === idx
                      ? att.success
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30'
                        : 'bg-rose-950 text-rose-300 border border-rose-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {att.success ? (
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                  ) : (
                    <AlertTriangle className="w-3 h-3 text-rose-400" />
                  )}
                  Attempt #{att.attempt_number}
                </button>
              ))}
            </div>
          )}

          {/* Copy Button */}
          <button
            onClick={copyToClipboard}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Code Body */}
      <div className="p-4 overflow-x-auto max-h-[380px] bg-[#050914] text-xs font-mono">
        <pre className="text-slate-300 whitespace-pre">
          <code>{displayCode}</code>
        </pre>
      </div>

      {/* Footer Audit Bar */}
      {currentAttempt && (
        <div className="p-2.5 border-t border-slate-800/80 bg-slate-950/60 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <div className="flex items-center gap-2">
            <Shield className="w-3.5 h-3.5 text-cyan-400" />
            <span>AST Policy: Compliant (Whitelisted Modules Only)</span>
          </div>
          <span>Execution Time: {currentAttempt.duration_ms}ms</span>
        </div>
      )}
    </div>
  );
}
