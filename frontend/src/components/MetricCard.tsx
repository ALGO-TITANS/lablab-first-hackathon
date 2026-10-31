import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: string;
  trend?: 'up' | 'down' | 'neutral';
  accent?: 'cyan' | 'blue' | 'emerald' | 'amber' | 'rose';
}

export default function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  accent = 'cyan',
}: MetricCardProps) {
  const accentStyles = {
    cyan: {
      border: 'border-cyan-500/20 hover:border-cyan-500/40',
      iconBg: 'bg-cyan-950/60 text-cyan-400 border border-cyan-500/30',
      glow: 'group-hover:shadow-[0_0_25px_rgba(6,182,212,0.15)]',
    },
    blue: {
      border: 'border-blue-500/20 hover:border-blue-500/40',
      iconBg: 'bg-blue-950/60 text-blue-400 border border-blue-500/30',
      glow: 'group-hover:shadow-[0_0_25px_rgba(59,130,246,0.15)]',
    },
    emerald: {
      border: 'border-emerald-500/20 hover:border-emerald-500/40',
      iconBg: 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/30',
      glow: 'group-hover:shadow-[0_0_25px_rgba(16,185,129,0.15)]',
    },
    amber: {
      border: 'border-amber-500/20 hover:border-amber-500/40',
      iconBg: 'bg-amber-950/60 text-amber-400 border border-amber-500/30',
      glow: 'group-hover:shadow-[0_0_25px_rgba(245,158,11,0.15)]',
    },
    rose: {
      border: 'border-rose-500/20 hover:border-rose-500/40',
      iconBg: 'bg-rose-950/60 text-rose-400 border border-rose-500/30',
      glow: 'group-hover:shadow-[0_0_25px_rgba(244,63,94,0.15)]',
    },
  }[accent];

  return (
    <div className={`group relative rounded-xl bg-[#0a1128]/70 backdrop-blur-md p-5 border ${accentStyles.border} transition-all duration-300 ${accentStyles.glow}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`p-2 rounded-lg ${accentStyles.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-white font-mono">{value}</span>
        {badge && (
          <span className="text-[11px] px-2 py-0.5 rounded-full font-medium bg-slate-800 text-slate-300 border border-slate-700">
            {badge}
          </span>
        )}
      </div>

      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
}
