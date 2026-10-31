'use client';

import React, { useEffect, useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Cpu, 
  ShieldCheck, 
  Key, 
  Check, 
  Loader2, 
  AlertCircle,
  Save,
  Server
} from 'lucide-react';
import { api } from '@/lib/api';
import { AppSettings } from '@/lib/types';

export default function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Form states
  const [provider, setProvider] = useState('mock');
  const [geminiKey, setGeminiKey] = useState('');
  const [geminiModel, setGeminiModel] = useState('gemini-2.0-flash');
  const [openaiKey, setOpenAIKey] = useState('');
  const [openaiBaseUrl, setOpenAIBaseUrl] = useState('https://api.openai.com/v1');
  const [openaiModel, setOpenAIModel] = useState('gpt-4o-mini');
  const [timeoutSeconds, setTimeoutSeconds] = useState(8.0);

  useEffect(() => {
    async function loadSettings() {
      setLoading(true);
      try {
        const data = await api.getSettings();
        setSettings(data);
        setProvider(data.default_llm_provider);
        setGeminiModel(data.gemini_model);
        setOpenAIBaseUrl(data.openai_base_url);
        setOpenAIModel(data.openai_model);
        setTimeoutSeconds(data.sandbox_timeout_seconds);
      } catch (err: any) {
        setStatusMessage({ type: 'error', text: err.message || 'Failed to load settings.' });
      } finally {
        setLoading(false);
      }
    }
    loadSettings();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setStatusMessage(null);

    try {
      const updated = await api.updateSettings({
        default_llm_provider: provider,
        gemini_api_key: geminiKey || undefined,
        gemini_model: geminiModel,
        openai_api_key: openaiKey || undefined,
        openai_base_url: openaiBaseUrl,
        openai_model: openaiModel,
        sandbox_timeout_seconds: Number(timeoutSeconds),
      });
      setSettings(updated);
      setStatusMessage({ type: 'success', text: 'Settings updated and saved successfully!' });
      setTimeout(() => setStatusMessage(null), 4000);
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to update settings.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[40vh] space-y-3">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-xs text-slate-400 font-mono">Loading configuration status...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Title */}
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-bold text-white tracking-tight">AI Provider & Sandbox Configuration</h1>
        <p className="text-xs text-slate-400 font-mono mt-0.5">
          Provider Abstraction Layer · Zero-Trust Execution Guardrails
        </p>
      </div>

      {statusMessage && (
        <div
          className={`flex items-center gap-3 p-4 rounded-xl text-xs font-mono border ${
            statusMessage.type === 'success'
              ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
              : 'bg-rose-950/50 border-rose-500/40 text-rose-300'
          }`}
        >
          {statusMessage.type === 'success' ? (
            <Check className="w-4 h-4 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Provider Selection */}
        <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-white">Active LLM Provider Engine</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Mock Provider */}
            <label
              className={`flex flex-col p-4 rounded-xl border cursor-pointer transition-all ${
                provider === 'mock'
                  ? 'bg-cyan-950/50 border-cyan-500/60 shadow-lg shadow-cyan-500/10'
                  : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
              }`}
            >
              <input
                type="radio"
                name="provider"
                value="mock"
                checked={provider === 'mock'}
                onChange={(e) => setProvider(e.target.value)}
                className="hidden"
              />
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-xs text-white">Mock / Demo</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/30 font-mono">
                  Offline Ready
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed mt-1">
                Guaranteed zero-API-cost provider. Perfect for deterministic testing and hackathon evaluation.
              </p>
            </label>

            {/* Google Gemini */}
            <label
              className={`flex flex-col p-4 rounded-xl border cursor-pointer transition-all ${
                provider === 'gemini'
                  ? 'bg-cyan-950/50 border-cyan-500/60 shadow-lg shadow-cyan-500/10'
                  : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
              }`}
            >
              <input
                type="radio"
                name="provider"
                value="gemini"
                checked={provider === 'gemini'}
                onChange={(e) => setProvider(e.target.value)}
                className="hidden"
              />
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-xs text-white">Google Gemini</span>
                <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                  settings?.gemini_api_key_configured
                    ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                    : 'bg-slate-800 text-slate-500'
                }`}>
                  {settings?.gemini_api_key_configured ? 'Key Configured' : 'Needs Key'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed mt-1">
                Powered by Gemini 2.0 Flash for ultra-fast Pandas reasoning and error diagnosis.
              </p>
            </label>

            {/* OpenAI / Compatible */}
            <label
              className={`flex flex-col p-4 rounded-xl border cursor-pointer transition-all ${
                provider === 'openai'
                  ? 'bg-cyan-950/50 border-cyan-500/60 shadow-lg shadow-cyan-500/10'
                  : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
              }`}
            >
              <input
                type="radio"
                name="provider"
                value="openai"
                checked={provider === 'openai'}
                onChange={(e) => setProvider(e.target.value)}
                className="hidden"
              />
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-xs text-white">OpenAI / Groq</span>
                <span className={`text-[10px] px-2 py-0.5 rounded font-mono ${
                  settings?.openai_api_key_configured
                    ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/30'
                    : 'bg-slate-800 text-slate-500'
                }`}>
                  {settings?.openai_api_key_configured ? 'Key Configured' : 'Needs Key'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed mt-1">
                Supports OpenAI, Groq (LLaMA 3.3), Ollama, and custom vLLM server endpoints.
              </p>
            </label>
          </div>
        </div>

        {/* Gemini Settings */}
        {provider === 'gemini' && (
          <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 p-6 space-y-4">
            <h4 className="text-xs font-semibold text-cyan-400 uppercase tracking-wider font-mono">
              Google Gemini Parameters
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Gemini API Key</label>
                <input
                  type="password"
                  placeholder={settings?.gemini_api_key_configured ? '••••••••••••••••' : 'AIzaSy...'}
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Model Name</label>
                <input
                  type="text"
                  value={geminiModel}
                  onChange={(e) => setGeminiModel(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>
            </div>
          </div>
        )}

        {/* OpenAI / Groq Settings */}
        {provider === 'openai' && (
          <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 p-6 space-y-4">
            <h4 className="text-xs font-semibold text-blue-400 uppercase tracking-wider font-mono">
              OpenAI / Groq API Parameters
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-1">
                <label className="text-xs text-slate-300">API Key</label>
                <input
                  type="password"
                  placeholder={settings?.openai_api_key_configured ? '••••••••••••••••' : 'sk-...'}
                  value={openaiKey}
                  onChange={(e) => setOpenAIKey(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Base URL</label>
                <input
                  type="text"
                  value={openaiBaseUrl}
                  onChange={(e) => setOpenAIBaseUrl(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Model Name</label>
                <input
                  type="text"
                  value={openaiModel}
                  onChange={(e) => setOpenAIModel(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                />
              </div>
            </div>
          </div>
        )}

        {/* Sandbox Guardrails */}
        <div className="rounded-xl border border-slate-800 bg-[#0a1128]/70 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-white">Execution Worker Sandbox Guardrails</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
            <div className="space-y-1">
              <label className="text-slate-300">Hard Timeout (seconds)</label>
              <input
                type="number"
                step="0.5"
                min="2.0"
                max="30.0"
                value={timeoutSeconds}
                onChange={(e) => setTimeoutSeconds(parseFloat(e.target.value) || 8.0)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div className="space-y-1">
              <label className="text-slate-400">Memory Cap (MB)</label>
              <input
                type="text"
                disabled
                value="512 MB (Enforced)"
                className="w-full px-3 py-2 rounded-lg bg-slate-950/60 border border-slate-800/80 text-slate-500"
              />
            </div>
            <div className="space-y-1">
              <label className="text-slate-400">Max Auto-Repairs</label>
              <input
                type="text"
                disabled
                value="2 Attempts"
                className="w-full px-3 py-2 rounded-lg bg-slate-950/60 border border-slate-800/80 text-slate-500"
              />
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs shadow-md shadow-cyan-500/20 transition-all hover:scale-[1.02] disabled:opacity-50"
          >
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Saving Configuration...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save Configuration</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
