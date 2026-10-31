'use client';

import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { 
  BarChart2, 
  TrendingUp, 
  PieChart as PieIcon, 
  Table as TableIcon,
  Download, 
  Sparkles 
} from 'lucide-react';

interface ChartRendererProps {
  chartType: 'bar' | 'line' | 'pie' | 'area' | 'scatter' | 'none';
  data: Record<string, any>[];
  query: string;
}

const COLORS = ['#06b6d4', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6'];

export default function ChartRenderer({ chartType, data, query }: ChartRendererProps) {
  const [activeTab, setActiveTab] = useState<'chart' | 'table'>('chart');
  const [selectedChartType, setSelectedChartType] = useState<string>(chartType || 'bar');

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-[#0a1128]/50 p-8 text-center text-slate-400 text-sm">
        No tabular or numerical data available to render charts.
      </div>
    );
  }

  // Derive keys for axes
  const sample = data[0] || {};
  const keys = Object.keys(sample);

  // Pick suitable X key (string / category) and Y key (number)
  let xKey = keys.find((k) => typeof sample[k] === 'string') || keys[0];
  let yKeys = keys.filter((k) => typeof sample[k] === 'number');

  if (yKeys.length === 0) {
    // If no numbers detected, try to parse
    yKeys = keys.filter((k) => k !== xKey);
  }

  const primaryY = yKeys[0] || keys[1] || keys[0];

  // Export CSV
  const handleDownloadCSV = () => {
    if (!data.length) return;
    const header = Object.keys(data[0]).join(',');
    const rows = data.map((row) =>
      Object.values(row)
        .map((v) => `"${String(v).replace(/"/g, '""')}"`)
        .join(',')
    );
    const csvContent = [header, ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `analysis_result_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Custom Dark Tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg bg-slate-900/95 border border-cyan-500/40 p-3 shadow-xl backdrop-blur-md text-xs font-mono">
          <p className="font-semibold text-white mb-1.5">{label || payload[0]?.name}</p>
          {payload.map((entry: any, index: number) => (
            <p key={`item-${index}`} style={{ color: entry.color || '#22d3ee' }}>
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 backdrop-blur-md overflow-hidden">
      {/* Visualizer Header */}
      <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-900/40">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <h4 className="text-sm font-semibold text-white">Visual Analytics & Data Output</h4>
        </div>

        <div className="flex items-center gap-2">
          {/* Chart Type Selector */}
          <div className="flex items-center rounded-lg bg-slate-950 p-1 border border-slate-800 text-xs">
            <button
              onClick={() => { setSelectedChartType('bar'); setActiveTab('chart'); }}
              className={`p-1.5 rounded transition-all ${
                activeTab === 'chart' && selectedChartType === 'bar'
                  ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Bar Chart"
            >
              <BarChart2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => { setSelectedChartType('line'); setActiveTab('chart'); }}
              className={`p-1.5 rounded transition-all ${
                activeTab === 'chart' && selectedChartType === 'line'
                  ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Line Chart"
            >
              <TrendingUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => { setSelectedChartType('pie'); setActiveTab('chart'); }}
              className={`p-1.5 rounded transition-all ${
                activeTab === 'chart' && selectedChartType === 'pie'
                  ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Pie Chart"
            >
              <PieIcon className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setActiveTab('table')}
              className={`p-1.5 rounded transition-all ${
                activeTab === 'table'
                  ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-white'
              }`}
              title="Result Table"
            >
              <TableIcon className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Download CSV */}
          <button
            onClick={handleDownloadCSV}
            className="flex items-center gap-1.5 text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-5">
        {activeTab === 'chart' ? (
          <div className="h-[340px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              {selectedChartType === 'line' ? (
                <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey={xKey} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
                  {yKeys.map((k, idx) => (
                    <Line
                      key={k}
                      type="monotone"
                      dataKey={k}
                      stroke={COLORS[idx % COLORS.length]}
                      strokeWidth={2.5}
                      dot={{ r: 4, fill: COLORS[idx % COLORS.length] }}
                      activeDot={{ r: 6 }}
                    />
                  ))}
                </LineChart>
              ) : selectedChartType === 'pie' ? (
                <PieChart>
                  <Pie
                    data={data}
                    dataKey={primaryY}
                    nameKey={xKey}
                    cx="50%"
                    cy="50%"
                    outerRadius={110}
                    innerRadius={50}
                    paddingAngle={4}
                    label={({ name, percent }: any) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                  >
                    {data.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
                </PieChart>
              ) : selectedChartType === 'area' ? (
                <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey={xKey} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey={primaryY}
                    stroke="#06b6d4"
                    fill="url(#colorCyan)"
                    fillOpacity={0.4}
                  />
                </AreaChart>
              ) : (
                <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey={xKey} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
                  {yKeys.map((k, idx) => (
                    <Bar
                      key={k}
                      dataKey={k}
                      fill={COLORS[idx % COLORS.length]}
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="overflow-x-auto max-h-[340px]">
            <table className="w-full text-left border-collapse text-xs">
              <thead className="sticky top-0 bg-[#0a1128] border-b border-slate-800 text-slate-300 font-medium">
                <tr>
                  {keys.map((k) => (
                    <th key={k} className="py-2.5 px-3 whitespace-nowrap font-mono text-cyan-300">
                      {k}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-850/50">
                    {keys.map((k) => (
                      <td key={k} className="py-2 px-3 whitespace-nowrap text-slate-300">
                        {row[k] !== null && row[k] !== undefined ? String(row[k]) : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
