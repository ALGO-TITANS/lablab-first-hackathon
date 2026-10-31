import {
  Dataset,
  DatasetListItem,
  DatasetPreview,
  AnalysisResult,
  AnalysisHistoryItem,
  DashboardMetrics,
  AppSettings
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Accept': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const err = await res.json();
      errorDetail = err.detail || errorDetail;
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Health
  checkHealth: () => fetchJson<{ status: string; app: string; default_provider: string }>('/api/health'),

  // Datasets
  uploadCsv: async (file: File): Promise<Dataset> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/api/datasets/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  listDatasets: (): Promise<DatasetListItem[]> => fetchJson<DatasetListItem[]>('/api/datasets'),

  getDataset: (id: string): Promise<Dataset> => fetchJson<Dataset>(`/api/datasets/${id}`),

  getDatasetPreview: (id: string, limit = 50): Promise<DatasetPreview> =>
    fetchJson<DatasetPreview>(`/api/datasets/${id}/preview?limit=${limit}`),

  deleteDataset: (id: string): Promise<{ message: string }> =>
    fetchJson<{ message: string }>(`/api/datasets/${id}`, { method: 'DELETE' }),

  loadSampleDataset: (sampleName: 'sales' | 'churn'): Promise<Dataset> =>
    fetchJson<Dataset>(`/api/datasets/load-sample/${sampleName}`, { method: 'POST' }),

  // Analysis
  runQuery: (datasetId: string, query: string, demoForceError = false, provider?: string): Promise<AnalysisResult> =>
    fetchJson<AnalysisResult>('/api/analysis/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dataset_id: datasetId,
        query,
        demo_force_error: demoForceError,
        provider,
      }),
    }),

  getHistory: (datasetId?: string): Promise<AnalysisHistoryItem[]> =>
    fetchJson<AnalysisHistoryItem[]>(datasetId ? `/api/analysis/history?dataset_id=${datasetId}` : '/api/analysis/history'),

  getAnalysisDetails: (id: string): Promise<AnalysisResult> =>
    fetchJson<AnalysisResult>(`/api/analysis/${id}`),

  // Dashboard Stats
  getDashboardMetrics: (): Promise<DashboardMetrics> =>
    fetchJson<DashboardMetrics>('/api/stats/dashboard'),

  // Settings
  getSettings: (): Promise<AppSettings> =>
    fetchJson<AppSettings>('/api/settings'),

  updateSettings: (payload: Partial<AppSettings & { gemini_api_key?: string; openai_api_key?: string }>): Promise<AppSettings> =>
    fetchJson<AppSettings>('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
};
