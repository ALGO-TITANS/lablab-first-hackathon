'use client';

import React, { useEffect, useState, use } from 'react';
import Link from 'next/link';
import { 
  Sparkles, 
  Send, 
  Loader2, 
  Terminal, 
  Table, 
  Info, 
  AlertCircle, 
  Wrench, 
  CheckCircle2,
  FileSpreadsheet,
  Zap,
  ArrowLeft
} from 'lucide-react';
import { api } from '@/lib/api';
import { Dataset, DatasetPreview, AnalysisResult } from '@/lib/types';
import DatasetSummaryCard from '@/components/DatasetSummaryCard';
import DataPreviewTable from '@/components/DataPreviewTable';
import ExecutionTimeline from '@/components/ExecutionTimeline';
import CodeViewer from '@/components/CodeViewer';
import ChartRenderer from '@/components/ChartRenderer';
import ErrorDiagnosisCard from '@/components/ErrorDiagnosisCard';

export default function WorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const datasetId = resolvedParams.id;

  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [preview, setPreview] = useState<DatasetPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Analysis state
  const [query, setQuery] = useState('');
  const [demoForceError, setDemoForceError] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  // Active view tab: 'analysis' | 'preview' | 'schema'
  const [activeTab, setActiveTab] = useState<'analysis' | 'preview' | 'schema'>('analysis');

  useEffect(() => {
    async function loadDataset() {
      setLoading(true);
      setError(null);
      try {
        const [dsData, prevData] = await Promise.all([
          api.getDataset(datasetId),
          api.getDatasetPreview(datasetId, 50),
        ]);
        setDataset(dsData);
        setPreview(prevData);
      } catch (err: any) {
        setError(err.message || 'Failed to load dataset.');
      } finally {
        setLoading(false);
      }
    }
    loadDataset();
  }, [datasetId]);

  const handleRunQuery = async (customQuery?: string) => {
    const q = customQuery || query;
    if (!q.trim() || isAnalyzing) return;

    setIsAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);

    try {
      const res = await api.runQuery(datasetId, q, demoForceError);
      setAnalysisResult(res);
    } catch (err: any) {
      setAnalysisError(err.message || 'Analysis execution failed.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const sampleQuestions = [
    "What are the top 5 products ranked by total revenue?",
    "Show total revenue and profit compared by region",
    "Show monthly sales trends over time",
    "Are there any missing or null values in this dataset?",
    "What is the distribution of customer contract types?",
  ];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-3">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-xs text-slate-400 font-mono">Loading dataset schema and records...</p>
      </div>
    );
  }

  if (error || !dataset) {
    return (
      <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-8 text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
        <h3 className="text-lg font-bold text-white">Dataset Not Found</h3>
        <p className="text-xs text-slate-300">{error || 'Could not locate dataset.'}</p>
        <Link
          href="/upload"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-xs text-white hover:bg-slate-700"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Upload</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Workspace Top Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">{dataset.name}</h1>
              <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30 font-mono">
                {dataset.original_filename}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              {dataset.row_count.toLocaleString()} rows · {dataset.column_count} columns · Sandboxed Environment
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center rounded-lg bg-slate-900 p-1 border border-slate-800 text-xs">
          <button
            onClick={() => setActiveTab('analysis')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'analysis'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/30 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI Analyst</span>
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'preview'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/30 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Table className="w-3.5 h-3.5" />
            <span>Data Preview</span>
          </button>
          <button
            onClick={() => setActiveTab('schema')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'schema'
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/30 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            <span>Schema & Stats</span>
          </button>
        </div>
      </div>

      {/* TAB CONTENT: Preview */}
      {activeTab === 'preview' && preview && (
        <DataPreviewTable
          columns={preview.columns}
          rows={preview.rows}
          totalRows={preview.total_rows}
        />
      )}

      {/* TAB CONTENT: Schema */}
      {activeTab === 'schema' && (
        <DatasetSummaryCard dataset={dataset} />
      )}

      {/* TAB CONTENT: Conversational AI Analyst */}
      {activeTab === 'analysis' && (
        <div className="space-y-6">
          {/* Query Input Box */}
          <div className="rounded-2xl border border-cyan-500/30 bg-[#091026]/90 p-5 shadow-2xl backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-cyan-400 flex items-center gap-1.5 font-mono uppercase tracking-wider">
                <Sparkles className="w-4 h-4" />
                Conversational Data Analyst
              </span>

              {/* Differentiating Feature: Demo Force Error Toggle */}
              <label className="flex items-center gap-2 cursor-pointer select-none text-xs text-slate-300">
                <input
                  type="checkbox"
                  checked={demoForceError}
                  onChange={(e) => setDemoForceError(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0 focus:ring-offset-0 cursor-pointer"
                />
                <span className="flex items-center gap-1 text-[11px] font-mono text-amber-400 font-semibold bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/30">
                  <Wrench className="w-3 h-3" />
                  Simulate Runtime Failure (Self-Healing Demo)
                </span>
              </label>
            </div>

            {/* Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleRunQuery();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                placeholder="Ask any question about your data (e.g., 'What are the top 5 products by revenue?')..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={isAnalyzing}
                className="flex-1 bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 shadow-inner"
              />
              <button
                type="submit"
                disabled={isAnalyzing || !query.trim()}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-40 disabled:hover:scale-100"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Run Query</span>
                  </>
                )}
              </button>
            </form>

            {/* Quick Sample Questions Chips */}
            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="text-[11px] text-slate-500 font-mono">Suggested:</span>
              {sampleQuestions.map((sq, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setQuery(sq);
                    handleRunQuery(sq);
                  }}
                  disabled={isAnalyzing}
                  className="text-[11px] px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800/80 text-slate-400 hover:text-cyan-300 hover:border-cyan-500/40 transition-all font-mono"
                >
                  {sq}
                </button>
              ))}
            </div>
          </div>

          {/* Analysis Error Message */}
          {analysisError && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-rose-950/50 border border-rose-500/40 text-rose-300 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
              <span>{analysisError}</span>
            </div>
          )}

          {/* Running Spinner */}
          {isAnalyzing && (
            <div className="rounded-xl border border-cyan-500/20 bg-slate-900/40 p-8 text-center space-y-3">
              <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
              <p className="text-sm font-semibold text-white">
                Generating Python code & executing in sandbox...
              </p>
              <p className="text-xs text-slate-400 font-mono">
                AST Security Verification ➔ Subprocess Worker ➔ Self-Healing Recovery Monitor
              </p>
            </div>
          )}

          {/* ANALYSIS RESULTS SECTION */}
          {analysisResult && (
            <div className="space-y-6">
              {/* Natural Language Explanation Banner */}
              <div className="rounded-xl border border-cyan-500/30 bg-gradient-to-r from-cyan-950/40 via-blue-950/20 to-slate-900/40 p-5 backdrop-blur-md">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-500/30 mt-0.5">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">AI Data Analyst Findings</h3>
                    <p className="mt-1 text-xs text-slate-200 leading-relaxed font-sans">
                      {analysisResult.explanation}
                    </p>
                    <div className="mt-3 flex items-center gap-3 text-[11px] font-mono text-slate-400">
                      <span>Execution: {analysisResult.duration_ms}ms</span>
                      <span>·</span>
                      <span>Status: {analysisResult.status.toUpperCase()}</span>
                      {analysisResult.repair_attempts_count > 0 && (
                        <>
                          <span>·</span>
                          <span className="text-amber-400">
                            Auto-Repairs: {analysisResult.repair_attempts_count}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Side-by-Side Error Diagnosis Card (Shown when self-healed) */}
              {analysisResult.status === 'repaired' && analysisResult.attempts.length > 1 && (
                <ErrorDiagnosisCard
                  failedAttempt={analysisResult.attempts[0]}
                  repairedAttempt={analysisResult.attempts[analysisResult.attempts.length - 1]}
                />
              )}

              {/* Visual Analytics Chart Renderer */}
              {analysisResult.chart_data && analysisResult.chart_data.length > 0 && (
                <ChartRenderer
                  chartType={analysisResult.chart_type}
                  data={analysisResult.chart_data}
                  query={analysisResult.query}
                />
              )}

              {/* Execution Timeline (Module F) */}
              <ExecutionTimeline
                timeline={analysisResult.timeline}
                status={analysisResult.status}
                repairCount={analysisResult.repair_attempts_count}
              />

              {/* Python Code Viewer (Module E) */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-300 font-mono uppercase tracking-wider">
                    Isolated Worker Source Code & Audit
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">
                    Zero-Trust Python Execution
                  </span>
                </div>
                <CodeViewer
                  attempts={analysisResult.attempts}
                  finalCode={analysisResult.final_code}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
