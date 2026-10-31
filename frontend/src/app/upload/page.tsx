'use client';

import React from 'react';
import CsvUploader from '@/components/CsvUploader';
import { UploadCloud, ShieldCheck, Zap } from 'lucide-react';

export default function UploadPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Title */}
      <div className="space-y-2 text-center">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
          <Zap className="w-3.5 h-3.5" />
          <span>Zero-Trust CSV Processing Engine</span>
        </div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Upload Dataset for Analysis</h1>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Upload any CSV, TSV, or delimited file. The system validates file contents, detects encodings, extracts schema statistics, and loads it for natural language data science.
        </p>
      </div>

      {/* Main Upload Box */}
      <CsvUploader />

      {/* Security & Storage Banner */}
      <div className="rounded-xl border border-slate-800 bg-[#0a1128]/40 p-4 text-xs text-slate-400 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1 leading-relaxed">
          <p>
            <strong className="text-slate-200">Security Guarantee:</strong> All uploaded files undergo automated sanitization. Files are stored with cryptographically generated identifiers. Host environment variables and server secrets are never accessible to data processing routines.
          </p>
          <p className="text-slate-500 text-[11px]">
            <strong className="text-slate-400">Public Demo & Storage Notice:</strong> Uploaded datasets and analysis histories on this public portfolio instance reside in temporary ephemeral storage that resets when the service restarts. Arbitrary code execution is disabled on public instances to ensure hosting security; pre-loaded sample datasets showcase full analytics and self-healing.
          </p>
        </div>
      </div>
    </div>
  );
}
