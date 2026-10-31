import React from 'react';
import { 
  FileText, 
  Layers, 
  Hash, 
  Calendar, 
  AlertTriangle, 
  CopyCheck, 
  Cpu
} from 'lucide-react';
import { Dataset } from '@/lib/types';

interface DatasetSummaryCardProps {
  dataset: Dataset;
}

export default function DatasetSummaryCard({ dataset }: DatasetSummaryCardProps) {
  const { summary, columns } = dataset;

  return (
    <div className="space-y-4">
      {/* Overview Banner */}
      <div className="rounded-xl border border-cyan-500/20 bg-gradient-to-r from-cyan-950/40 via-blue-950/20 to-slate-900/40 p-5 backdrop-blur-md">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-500/30 flex-shrink-0 mt-0.5">
            <Cpu className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <span>Autonomous AI Data Understanding</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-500/40 text-cyan-300 font-mono">
                Verified Schema
              </span>
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              {summary.overview_text}
            </p>
          </div>
        </div>
      </div>

      {/* Grid of Dimension Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-lg bg-slate-900/60 border border-slate-800 p-3.5">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>Dimensions</span>
          </div>
          <p className="text-lg font-bold text-white font-mono">
            {dataset.row_count.toLocaleString()} <span className="text-xs font-normal text-slate-400">× {dataset.column_count} cols</span>
          </p>
        </div>

        <div className="rounded-lg bg-slate-900/60 border border-slate-800 p-3.5">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Hash className="w-3.5 h-3.5 text-blue-400" />
            <span>Numerical Features</span>
          </div>
          <p className="text-lg font-bold text-white font-mono">
            {summary.numerical_columns.length} <span className="text-xs font-normal text-slate-400">dimensions</span>
          </p>
        </div>

        <div className="rounded-lg bg-slate-900/60 border border-slate-800 p-3.5">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>Missing Values</span>
          </div>
          <p className="text-lg font-bold text-white font-mono">
            {summary.missing_cells} <span className="text-xs font-normal text-slate-400">({summary.missing_percentage}%)</span>
          </p>
        </div>

        <div className="rounded-lg bg-slate-900/60 border border-slate-800 p-3.5">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <CopyCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Duplicates</span>
          </div>
          <p className="text-lg font-bold text-white font-mono">
            {summary.duplicate_rows} <span className="text-xs font-normal text-slate-400">rows</span>
          </p>
        </div>
      </div>

      {/* Schema Attributes Breakdown */}
      <div className="rounded-xl border border-slate-800 bg-[#0a1128]/50 p-4">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
          Column Attributes & Type Spectrum
        </h4>
        <div className="flex flex-wrap gap-2">
          {columns.map((col) => (
            <div
              key={col.name}
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-slate-900/80 border border-slate-800 text-xs"
            >
              <span className="font-mono text-cyan-300 font-medium">{col.name}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                {col.data_type}
              </span>
              {col.null_count > 0 && (
                <span className="text-[10px] text-amber-400 font-mono">
                  {col.null_percentage}% null
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
