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

export type ReviewStatus =
  | 'pending_review'
  | 'under_review'
  | 'reviewed'
  | 'dismissed'
  | 'needs_investigation';

export interface FindingReviewHistoryItem {
  id: string;
  finding_id: string;
  action: string;
  previous_status: string;
  new_status: string;
  reviewer_id: string;
  notes?: string;
  dismissal_reason?: string;
  created_at: string;
}

export interface FindingDetailedItem {
  id: string;
  audit_id: string;
  answer_id: string;
  task_id: string;
  worker_id: string;
  check_identifier: string;
  finding_type: string;
  evidence_confidence: string;
  explanation: string;
  evidence_text?: string;
  evidence_offsets?: [number, number];
  numerical_measurements: Record<string, any>;
  related_answer_ids: string[];
  limitations: string;
  review_status: ReviewStatus;
  reviewer_notes?: string;
  assigned_reviewer?: string;
  reviewed_at?: string;
  created_at: string;
  worker_answer?: string;
  prompt?: string;
  history: FindingReviewHistoryItem[];
}

export interface ComparisonDiffSegment {
  text: string;
  is_match: boolean;
  is_source_only: boolean;
  is_target_only: boolean;
}

export interface SideBySideComparisonResponse {
  finding_id: string;
  task_id: string;
  worker_id: string;
  comparison_type: string;
  source_answer: string;
  target_answer: string;
  target_label: string;
  similarity_score?: number;
  measurements: Record<string, any>;
  explanation: string;
  diff_segments: ComparisonDiffSegment[];
  limitations: string;
}

export interface MarkerInvestigationItem {
  id: string;
  task_id: string;
  marker_id: string;
  expected_marker: string;
  detected: boolean;
  detected_marker?: string;
  location_in_answer?: [number, number];
  preparation_version: string;
  finding_id?: string;
}

export interface DuplicateClusterItem {
  cluster_id: string;
  task_id: string;
  worker_ids: string[];
  answer_ids: string[];
  representative_text: string;
  similarity_matrix: Record<string, number>;
  findings_count: number;
}

export interface InvestigationWorkspaceResponse {
  audit: {
    id: string;
    dataset_name: string;
    status: AuditStatus;
    answers_count: number;
    workers_count: number;
    flagged_workers_count: number;
    consent_external_ai: boolean;
    created_at: string;
    completed_at?: string;
    expires_at: string;
    owner_id?: string;
    summary_metrics: Record<string, any>;
  };
  findings: FindingDetailedItem[];
  markers: MarkerInvestigationItem[];
  duplicate_clusters: DuplicateClusterItem[];
  calibration?: {
    sample_size: number;
    flagged_count: number;
    estimated_fp_rate: number;
    ci_lower: number;
    ci_upper: number;
    ci_method: string;
  };
}

export interface HistogramBucket {
  bucket: string;
  min_val?: number;
  max_val?: number;
  count: number;
  percentage: number;
}

export interface WorkerContribution {
  worker_id: string;
  answer_count: number;
  percentage_of_total: number;
}

export interface QualityWarning {
  code: string;
  title: string;
  message: string;
  severity: 'critical' | 'warning' | 'info';
  affected_records: number;
}

export interface AnswerLengthStats {
  min_chars: number;
  max_chars: number;
  avg_chars: number;
  median_chars: number;
  min_words: number;
  max_words: number;
  avg_words: number;
  median_words: number;
  short_answers_count: number;
  long_answers_count: number;
}

export interface WorkerParticipationStats {
  min_answers: number;
  max_answers: number;
  avg_answers: number;
  median_answers: number;
  distribution_buckets: HistogramBucket[];
  top_contributors: WorkerContribution[];
}

export interface TaskCoverageStats {
  min_answers_per_task: number;
  max_answers_per_task: number;
  avg_answers_per_task: number;
  coverage_buckets: HistogramBucket[];
}

export interface SubmissionTimeStats {
  timestamps_present_count: number;
  timestamps_missing_count: number;
  timestamp_coverage_pct: number;
  hourly_distribution: Record<string, number>;
  avg_seconds_spent?: number;
  median_seconds_spent?: number;
}

export interface DatasetQualityResponse {
  audit_id: string;
  dataset_name: string;
  total_records: number;
  unique_workers: number;
  unique_tasks: number;
  completeness_score: number;
  empty_answers_count: number;
  missing_worker_ids_count: number;
  missing_timestamps_count: number;
  duplicate_task_submissions_count: number;
  duplicate_submissions_count: number;
  length_stats: AnswerLengthStats;
  length_distribution: HistogramBucket[];
  worker_participation: WorkerParticipationStats;
  task_coverage: TaskCoverageStats;
  submission_time_analysis: SubmissionTimeStats;
  warnings: QualityWarning[];
}
