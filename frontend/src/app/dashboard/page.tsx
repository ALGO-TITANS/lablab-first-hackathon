'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Database, 
  Search, 
  CheckCircle2, 
  Wrench, 
  AlertCircle, 
  Activity, 
  Sparkles, 
  ArrowRight,
  FileSpreadsheet,
  Clock,
  RefreshCw
} from 'lucide-react';
import MetricCard from '@/components/MetricCard';
import { api } from '@/lib/api';
import { DashboardMetrics } from '@/lib/types';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDashboardMetrics();
      setMetrics(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Analytics Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Telemetry & Telecommunications · Sandboxed Python Execution Engine
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white hover:border-slate-700 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <Link
            href="/upload"
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 transition-all hover:scale-[1.02]"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Upload New CSV</span>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Uploaded Datasets"
          value={metrics ? metrics.total_datasets : '0'}
          subtitle="Available for natural language querying"
          icon={Database}
          accent="cyan"
        />
        <MetricCard
          title="Analysis Queries"
          value={metrics ? metrics.total_queries : '0'}
          subtitle="Total executions completed"
          icon={Search}
          accent="blue"
        />
        <MetricCard
          title="Self-Healed Executions"
          value={metrics ? metrics.repaired_executions : '0'}
          subtitle="Errors detected and auto-repaired"
          icon={Wrench}
          accent="amber"
          badge="Autonomous"
        />
        <MetricCard
          title="Execution Worker"
          value={metrics ? metrics.ai_worker_status.split(' ')[0] : 'Online'}
          subtitle="Subprocess Sandbox with 8s limits"
          icon={Activity}
          accent="emerald"
          badge="Hardened"
        />
      </div>

      {/* Recent Datasets and Activity Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Datasets */}
        <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 backdrop-blur-md p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-semibold text-white">Recent Datasets</h3>
            </div>
            <Link
              href="/upload"
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-2.5">
            {metrics?.recent_datasets && metrics.recent_datasets.length > 0 ? (
              metrics.recent_datasets.map((ds) => (
                <Link
                  key={ds.id}
                  href={`/workspace/${ds.id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50 border border-slate-800/80 hover:border-cyan-500/40 hover:bg-slate-850/60 transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded bg-cyan-950/60 text-cyan-400 border border-cyan-500/20">
                      <FileSpreadsheet className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-white group-hover:text-cyan-300">
                        {ds.name}
                      </p>
                      <p className="text-[11px] text-slate-400 font-mono">
                        {ds.row_count.toLocaleString()} rows · {ds.column_count} columns
                      </p>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
                </Link>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-500">
                No datasets uploaded yet.{' '}
                <Link href="/upload" className="text-cyan-400 hover:underline">
                  Upload or load a sample dataset
                </Link>
                .
              </div>
            )}
          </div>
        </div>

        {/* Recent Analysis Activity */}
        <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 backdrop-blur-md p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-semibold text-white">Recent Analysis Sessions</h3>
            </div>
            <Link
              href="/history"
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium"
            >
              <span>View History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-2.5">
            {metrics?.recent_analyses && metrics.recent_analyses.length > 0 ? (
              metrics.recent_analyses.map((an) => (
                <div
                  key={an.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50 border border-slate-800/80"
                >
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-white line-clamp-1">
                      {an.query}
                    </p>
                    <p className="text-[11px] text-slate-400 font-mono">
                      Dataset: {an.dataset_name || 'Active CSV'} · {an.duration_ms}ms
                    </p>
                  </div>
                  <div>
                    {an.status === 'repaired' && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-500/30 font-mono">
                        Self-Healed
                      </span>
                    )}
                    {an.status === 'success' && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/30 font-mono">
                        Success
                      </span>
                    )}
                    {an.status === 'failed' && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-500/30 font-mono">
                        Failed
                      </span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="p-6 text-center text-xs text-slate-500">
                No analyses performed yet. Open a dataset to ask questions!
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
