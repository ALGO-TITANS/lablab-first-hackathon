'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  History as HistoryIcon, 
  Terminal, 
  Clock, 
  CheckCircle2, 
  Wrench, 
  AlertCircle, 
  ArrowRight,
  Database,
  Search,
  RefreshCw,
  Loader2
} from 'lucide-react';
import { api } from '@/lib/api';
import { AnalysisHistoryItem, AnalysisResult } from '@/lib/types';
import CodeViewer from '@/components/CodeViewer';
import ExecutionTimeline from '@/components/ExecutionTimeline';

export default function HistoryPage() {
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResult | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHistory();
      setHistory(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleInspect = async (id: string) => {
    setLoadingDetails(true);
    try {
      const details = await api.getAnalysisDetails(id);
      setSelectedAnalysis(details);
    } catch (err: any) {
      alert('Failed to load session details: ' + err.message);
    } finally {
      setLoadingDetails(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Execution History & Audit Log</h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Cryptographic Audit Trail · Past Analysis Inquiries & Recovery Attempts
          </p>
        </div>

        <button
          onClick={loadHistory}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] space-y-3">
          <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
          <p className="text-xs text-slate-400 font-mono">Loading history records...</p>
        </div>
      ) : history.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-[#0a1128]/50 p-12 text-center space-y-3">
          <HistoryIcon className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-white">No Execution Records Yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Once you analyze a dataset, all generated code, error traces, and self-healing timelines will be recorded here.
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 text-xs text-slate-950 font-bold"
          >
            Start First Analysis
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* History List */}
          <div className="lg:col-span-1 space-y-3">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono">
              Saved Sessions ({history.length})
            </h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {history.map((item) => {
                const isSelected = selectedAnalysis?.id === item.id;
                return (
                  <div
                    key={item.id}
                    onClick={() => handleInspect(item.id)}
                    className={`cursor-pointer rounded-xl p-3.5 border transition-all text-left ${
                      isSelected
                        ? 'bg-cyan-950/40 border-cyan-500/50 shadow-md shadow-cyan-500/10'
                        : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 hover:bg-slate-850/60'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className="text-[11px] font-mono text-cyan-400 font-medium truncate">
                        {item.dataset_name || 'Active CSV'}
                      </span>
                      {item.status === 'repaired' && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-500/30 font-mono">
                          Self-Healed
                        </span>
                      )}
                      {item.status === 'success' && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/30 font-mono">
                          Success
                        </span>
                      )}
                      {item.status === 'failed' && (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-500/30 font-mono">
                          Failed
                        </span>
                      )}
                    </div>
                    <p className="text-xs font-semibold text-white line-clamp-2 mb-2">
                      {item.query}
                    </p>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                      <span>{item.duration_ms}ms</span>
                      <span>{new Date(item.created_at).toLocaleTimeString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Detailed Inspector */}
          <div className="lg:col-span-2">
            {loadingDetails ? (
              <div className="rounded-xl border border-slate-800 bg-[#0a1128]/50 p-12 text-center">
                <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-2" />
                <p className="text-xs text-slate-400 font-mono">Loading full session details...</p>
              </div>
            ) : selectedAnalysis ? (
              <div className="space-y-6">
                <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-cyan-400">
                      Session ID: {selectedAnalysis.id.slice(0, 8)}...
                    </span>
                    <Link
                      href={`/workspace/${selectedAnalysis.dataset_id}`}
                      className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium"
                    >
                      <span>Open in Workspace</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                  <h3 className="text-base font-bold text-white">{selectedAnalysis.query}</h3>
                  <p className="text-xs text-slate-300">{selectedAnalysis.explanation}</p>
                </div>

                {/* Timeline */}
                <ExecutionTimeline
                  timeline={selectedAnalysis.timeline}
                  status={selectedAnalysis.status}
                  repairCount={selectedAnalysis.repair_attempts_count}
                />

                {/* Code */}
                <CodeViewer
                  attempts={selectedAnalysis.attempts}
                  finalCode={selectedAnalysis.final_code}
                />
              </div>
            ) : (
              <div className="rounded-xl border border-slate-800 bg-[#0a1128]/40 p-12 text-center text-slate-500 text-xs">
                Select an execution record from the list to view its complete timeline, code audit, and diagnosis history.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
