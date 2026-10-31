'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { 
  UploadCloud, 
  FileSpreadsheet, 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  Database,
  ArrowRight
} from 'lucide-react';
import { api } from '@/lib/api';

interface CsvUploaderProps {
  onUploadSuccess?: (datasetId: string) => void;
}

export default function CsvUploader({ onUploadSuccess }: CsvUploaderProps) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (file: File) => {
    setUploadError(null);

    // Validation
    const validExtensions = ['.csv', '.tsv', '.txt'];
    const hasValidExt = validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext));
    if (!hasValidExt) {
      setUploadError('Invalid file type. Please upload a valid .csv, .tsv, or delimited file.');
      return;
    }

    const maxSizeMb = 50;
    if (file.size > maxSizeMb * 1024 * 1024) {
      setUploadError(`File size exceeds the ${maxSizeMb}MB maximum limit.`);
      return;
    }

    setSelectedFile(file);
    setIsUploading(true);

    try {
      const dataset = await api.uploadCsv(file);
      if (onUploadSuccess) {
        onUploadSuccess(dataset.id);
      } else {
        router.push(`/workspace/${dataset.id}`);
      }
    } catch (err: any) {
      setUploadError(err.message || 'Failed to parse and upload CSV.');
      setIsUploading(false);
    }
  };

  const handleLoadSample = async (sampleType: 'sales' | 'churn') => {
    setUploadError(null);
    setIsUploading(true);
    try {
      const dataset = await api.loadSampleDataset(sampleType);
      if (onUploadSuccess) {
        onUploadSuccess(dataset.id);
      } else {
        router.push(`/workspace/${dataset.id}`);
      }
    } catch (err: any) {
      setUploadError(err.message || 'Failed to load sample dataset.');
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Drag & Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-8 sm:p-12 text-center transition-all duration-300 ${
          isDragging
            ? 'border-cyan-400 bg-cyan-950/40 shadow-[0_0_30px_rgba(6,182,212,0.2)]'
            : 'border-slate-800 bg-[#0a1128]/50 hover:border-cyan-500/50 hover:bg-[#0c1635]/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.tsv,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />

        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-950/70 border border-cyan-500/30 text-cyan-400 shadow-lg shadow-cyan-500/10 mb-4">
          <UploadCloud className={`h-8 w-8 ${isUploading ? 'animate-bounce' : ''}`} />
        </div>

        <h3 className="text-lg font-semibold text-white">
          {isUploading ? 'Validating and Parsing Dataset...' : 'Drag & Drop your CSV file here'}
        </h3>
        <p className="mt-2 text-sm text-slate-400 max-w-md mx-auto">
          Supports comma, semicolon, tab, and pipe-delimited datasets. Automatic encoding detection and schema extraction.
        </p>

        <div className="mt-5 flex items-center justify-center gap-2">
          <span className="text-xs px-3 py-1 rounded-full bg-slate-900 text-slate-400 border border-slate-800 font-mono">
            Max 50MB
          </span>
          <span className="text-xs px-3 py-1 rounded-full bg-slate-900 text-slate-400 border border-slate-800 font-mono">
            Auto-Sanitized
          </span>
          <span className="text-xs px-3 py-1 rounded-full bg-slate-900 text-slate-400 border border-slate-800 font-mono">
            Zero-Trust Isolation
          </span>
        </div>
      </div>

      {/* Error Message */}
      {uploadError && (
        <div className="flex items-center gap-3 p-4 rounded-xl bg-rose-950/50 border border-rose-500/40 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* 1-Click Sample Datasets for Hackathon Evaluators */}
      <div className="rounded-xl border border-cyan-950/60 bg-[#0a1128]/40 p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <h4 className="text-sm font-semibold text-white">Instant Hackathon Testing Datasets</h4>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">Pre-loaded & Verified</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            onClick={() => handleLoadSample('sales')}
            disabled={isUploading}
            className="flex items-center justify-between p-3.5 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-850 text-left transition-all group disabled:opacity-50"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/30">
                <FileSpreadsheet className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-semibold text-white group-hover:text-cyan-300">
                  Global Sales & Revenue
                </p>
                <p className="text-[11px] text-slate-400">13 columns · Technology, Furniture & Office Supplies</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
          </button>

          <button
            onClick={() => handleLoadSample('churn')}
            disabled={isUploading}
            className="flex items-center justify-between p-3.5 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-850 text-left transition-all group disabled:opacity-50"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded bg-blue-950 text-blue-400 border border-blue-500/30">
                <Database className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-semibold text-white group-hover:text-blue-300">
                  Customer Churn & Retention
                </p>
                <p className="text-[11px] text-slate-400">10 columns · Contracts, charges, and churn status</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all" />
          </button>
        </div>
      </div>
    </div>
  );
}
