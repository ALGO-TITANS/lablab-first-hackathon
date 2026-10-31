export interface ColumnMeta {
  name: string;
  data_type: string;
  non_null_count: number;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  sample_values: (string | number | boolean | null)[];
  is_numeric: boolean;
  is_datetime: boolean;
  is_categorical: boolean;
  stats?: {
    min?: number;
    max?: number;
    mean?: number;
    median?: number;
    std?: number;
    top_frequencies?: Record<string, number>;
  };
}

export interface DatasetSummary {
  total_rows: number;
  total_columns: number;
  total_cells: number;
  missing_cells: number;
  missing_percentage: number;
  duplicate_rows: number;
  numerical_columns: string[];
  categorical_columns: string[];
  datetime_columns: string[];
  overview_text: string;
}

export interface Dataset {
  id: string;
  name: string;
  original_filename: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  columns: ColumnMeta[];
  summary: DatasetSummary;
  created_at: string;
}

export interface DatasetListItem {
  id: string;
  name: string;
  original_filename: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  created_at: string;
}

export interface DatasetPreview {
  id: string;
  name: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  rows: Record<string, any>[];
}

export interface TimelineStep {
  step: string;
  status: 'completed' | 'running' | 'failed' | 'skipped' | 'warning';
  message: string;
  timestamp: string;
  details?: Record<string, any>;
}

export interface ExecutionAttempt {
  attempt_number: number;
  code: string;
  success: boolean;
  error_type?: string;
  error_message?: string;
  error_traceback?: string;
  diagnosis?: string;
  duration_ms: number;
}

export interface AnalysisResult {
  id: string;
  dataset_id: string;
  query: string;
  status: 'success' | 'repaired' | 'failed';
  duration_ms: number;
  repair_attempts_count: number;
  final_code: string;
  explanation: string;
  chart_type: 'bar' | 'line' | 'pie' | 'area' | 'scatter' | 'none';
  chart_data?: Record<string, any>[];
  result_table?: Record<string, any>[];
  summary_stats?: Record<string, any>;
  timeline: TimelineStep[];
  attempts: ExecutionAttempt[];
  created_at: string;
}

export interface AnalysisHistoryItem {
  id: string;
  dataset_id: string;
  dataset_name?: string;
  query: string;
  status: string;
  duration_ms: number;
  repair_attempts_count: number;
  chart_type?: string;
  created_at: string;
}

export interface DashboardMetrics {
  total_datasets: number;
  total_queries: number;
  successful_executions: number;
  repaired_executions: number;
  failed_executions: number;
  total_successful_with_repairs: number;
  recent_datasets: DatasetListItem[];
  recent_analyses: AnalysisHistoryItem[];
  ai_worker_status: string;
}

export interface AppSettings {
  default_llm_provider: string;
  gemini_api_key_configured: boolean;
  gemini_model: string;
  openai_api_key_configured: boolean;
  openai_base_url: string;
  openai_model: string;
  sandbox_timeout_seconds: number;
  sandbox_max_memory_mb: number;
  sandbox_max_output_chars: number;
  max_repair_attempts: number;
}
