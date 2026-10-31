import React from 'react';
import { 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Sparkles, 
  Wrench, 
  ShieldCheck, 
  FileCode, 
  Activity,
  ChevronDown
} from 'lucide-react';
import { TimelineStep } from '@/lib/types';

interface ExecutionTimelineProps {
  timeline: TimelineStep[];
  status: 'success' | 'repaired' | 'failed';
  repairCount: number;
}

export default function ExecutionTimeline({ timeline, status, repairCount }: ExecutionTimelineProps) {
  const getStepIcon = (stepName: string, stepStatus: string) => {
    if (stepStatus === 'running') {
      return <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />;
    }
    if (stepStatus === 'failed') {
      return <AlertCircle className="w-4 h-4 text-rose-400" />;
    }
    if (stepStatus === 'warning') {
      return <AlertCircle className="w-4 h-4 text-amber-400" />;
    }

    if (stepName.includes('Understanding')) return <Sparkles className="w-4 h-4 text-blue-400" />;
    if (stepName.includes('Generating')) return <FileCode className="w-4 h-4 text-indigo-400" />;
    if (stepName.includes('Validating')) return <ShieldCheck className="w-4 h-4 text-cyan-400" />;
    if (stepName.includes('Executing')) return <Activity className="w-4 h-4 text-emerald-400" />;
    if (stepName.includes('Repairing') || stepName.includes('Detecting')) return <Wrench className="w-4 h-4 text-amber-400" />;

    return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
  };

  const getStatusBadge = (stepStatus: string) => {
    switch (stepStatus) {
      case 'completed':
        return <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 font-mono">Passed</span>;
      case 'warning':
        return <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-500/30 font-mono">Recovering</span>;
      case 'failed':
        return <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950/80 text-rose-400 border border-rose-500/30 font-mono">Failed</span>;
      case 'running':
        return <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-500/30 font-mono">In Progress</span>;
      default:
        return null;
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 backdrop-blur-md p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h4 className="text-sm font-semibold text-white">Execution & Recovery Timeline</h4>
        </div>
        <div className="flex items-center gap-2">
          {status === 'repaired' && (
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-950 border border-amber-500/40 text-amber-300 font-mono flex items-center gap-1.5 animate-pulse">
              <Wrench className="w-3 h-3" />
              Self-Healed ({repairCount} {repairCount === 1 ? 'repair' : 'repairs'})
            </span>
          )}
          {status === 'success' && (
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-950 border border-emerald-500/40 text-emerald-300 font-mono flex items-center gap-1.5">
              <CheckCircle2 className="w-3 h-3" />
              Direct Execution Pass
            </span>
          )}
          {status === 'failed' && (
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-rose-950 border border-rose-500/40 text-rose-300 font-mono flex items-center gap-1.5">
              <AlertCircle className="w-3 h-3" />
              Execution Failed
            </span>
          )}
        </div>
      </div>

      {/* Timeline Steps */}
      <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {timeline.map((item, idx) => {
          const isWarning = item.status === 'warning';
          const isFailed = item.status === 'failed';

          return (
            <div key={idx} className="relative group">
              {/* Node Icon */}
              <div className={`absolute -left-6 top-0.5 h-5 w-5 rounded-full flex items-center justify-center border ${
                isFailed ? 'bg-rose-950 border-rose-500 text-rose-400' :
                isWarning ? 'bg-amber-950 border-amber-500 text-amber-400' :
                'bg-slate-900 border-slate-700 text-cyan-400'
              }`}>
                {getStepIcon(item.step, item.status)}
              </div>

              <div className={`rounded-lg p-3 border transition-all ${
                isWarning ? 'bg-amber-950/20 border-amber-500/30' :
                isFailed ? 'bg-rose-950/20 border-rose-500/30' :
                'bg-slate-900/40 border-slate-800/80 hover:border-slate-700'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-white flex items-center gap-2">
                    {item.step}
                  </span>
                  {getStatusBadge(item.status)}
                </div>

                <p className="mt-1 text-xs text-slate-300 leading-relaxed">
                  {item.message}
                </p>

                {item.details && (
                  <div className="mt-2 text-[11px] font-mono p-2 rounded bg-black/40 border border-slate-800/80 text-slate-400 overflow-x-auto">
                    {item.details.traceback && (
                      <pre className="text-rose-300 whitespace-pre-wrap">{item.details.traceback}</pre>
                    )}
                    {item.details.initial_code_preview && (
                      <pre className="text-cyan-300 whitespace-pre-wrap">{item.details.initial_code_preview}</pre>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
