export type CheckIdentifier = 'marker' | 'similarity' | 'duplicates' | 'speed';

export type EvidenceConfidence = 'High' | 'Medium' | 'Low';

export type AuditStatus =
  | 'queued'
  | 'validating'
  | 'running'
  | 'partially_completed'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'expired';

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  queue: string;
  environment: string;
}

export interface PreparedTask {
  task_id: string;
  prompt: string;
  marker: string;
  hiding_method: string;
  prepared_prompt: string;
  visible_preview: string;
  model_received_preview: string;
}

export interface MarkerManifest {
  format_version: string;
  created_at: string;
  items: Array<{
    task_id: string;
    marker: string;
    hiding_method: string;
  }>;
}

export interface Finding {
  id: string;
  task_id: string;
  worker_id: string;
  check_identifier: CheckIdentifier;
  finding_type: string;
  evidence_confidence: EvidenceConfidence;
  explanation: string;
  evidence_text?: string;
  evidence_offsets?: [number, number];
  numerical_measurements?: Record<string, number | string>;
  related_answer_ids?: string[];
  created_at?: string;
}

export interface AuditSummary {
  audit_id: string;
  status: AuditStatus;
  answers_count: number;
  workers_count: number;
  flagged_workers_count: number;
  created_at: string;
  completed_at?: string;
  expires_at: string;
  confidence_counts: {
    High: number;
    Medium: number;
    Low: number;
  };
  check_statuses: Record<CheckIdentifier, {
    status: string;
    findings_count: number;
    error_message?: string;
  }>;
  calibration?: {
    sample_size: number;
    flagged_count: number;
    estimated_fp_rate: number;
    ci_lower: number;
    ci_upper: number;
    ci_method: string;
  };
}

export interface ValidationResult {
  valid: boolean;
  total_rows: number;
  tasks_count: number;
  workers_count: number;
  errors: Array<{
    row?: number;
    field?: string;
    message: string;
  }>;
  warnings: Array<{
    row?: number;
    field?: string;
    message: string;
  }>;
  preview: Array<Record<string, unknown>>;
  detected_columns: string[];
}

export interface DashboardStats {
  total_audits: number;
  completed_audits: number;
  running_audits: number;
  failed_audits: number;
  total_answers_analyzed: number;
  findings_requiring_review: number;
  reviewed_findings: number;
  high_confidence_findings: number;
  medium_confidence_findings: number;
  low_confidence_findings: number;
  findings_by_category: Record<string, number>;
  audits_by_status: Record<string, number>;
  activity_over_time: Array<{
    date: string;
    audits: number;
    findings: number;
  }>;
  dataset_size_distribution: Record<string, number>;
}

export interface DashboardAuditItem {
  id: string;
  dataset_name: string;
  status: AuditStatus;
  answers_count: number;
  workers_count: number;
  flagged_workers_count: number;
  findings_count: number;
  created_at: string;
  completed_at?: string;
  duration_seconds?: number;
  expires_at: string;
  owner_id?: string;
}

export interface DashboardAuditsResponse {
  items: DashboardAuditItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

