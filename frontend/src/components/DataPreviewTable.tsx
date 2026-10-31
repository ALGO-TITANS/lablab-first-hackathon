'use client';

import React, { useState } from 'react';
import { Search, ChevronLeft, ChevronRight, Table } from 'lucide-react';

interface DataPreviewTableProps {
  columns: string[];
  rows: Record<string, any>[];
  totalRows: number;
}

export default function DataPreviewTable({ columns, rows, totalRows }: DataPreviewTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 10;

  // Filter rows by search term
  const filteredRows = rows.filter((row) =>
    Object.values(row).some((val) =>
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const totalPages = Math.ceil(filteredRows.length / rowsPerPage) || 1;
  const startIndex = (currentPage - 1) * rowsPerPage;
  const visibleRows = filteredRows.slice(startIndex, startIndex + rowsPerPage);

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 backdrop-blur-md overflow-hidden">
      {/* Header bar */}
      <div className="p-4 border-b border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-900/40">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-cyan-400" />
          <h4 className="text-sm font-semibold text-white">Dataset Records Preview</h4>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
            Showing {Math.min(rows.length, totalRows)} of {totalRows.toLocaleString()} rows
          </span>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search preview rows..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-slate-950/70 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-[420px]">
        <table className="w-full text-left border-collapse text-xs">
          <thead className="sticky top-0 bg-[#0a1128] border-b border-slate-800 text-slate-300 font-medium">
            <tr>
              <th className="py-2.5 px-3.5 font-mono text-slate-500 w-12">#</th>
              {columns.map((col) => (
                <th key={col} className="py-2.5 px-3.5 whitespace-nowrap font-mono text-cyan-300">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {visibleRows.length > 0 ? (
              visibleRows.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-850/50 transition-colors">
                  <td className="py-2 px-3.5 text-slate-600 select-none">
                    {startIndex + idx + 1}
                  </td>
                  {columns.map((col) => (
                    <td key={col} className="py-2 px-3.5 whitespace-nowrap text-slate-300">
                      {row[col] !== null && row[col] !== undefined ? String(row[col]) : (
                        <span className="text-slate-600 italic">null</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length + 1} className="py-8 text-center text-slate-500">
                  No matching records found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 bg-slate-900/30">
        <span>
          Page {currentPage} of {totalPages}
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
            disabled={currentPage === 1}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="p-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
