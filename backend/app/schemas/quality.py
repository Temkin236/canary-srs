from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class HistogramBucket(BaseModel):
    bucket: str
    min_val: int
    max_val: Optional[int] = None
    count: int
    percentage: float


class WorkerContribution(BaseModel):
    worker_id: str
    answer_count: int
    percentage_of_total: float


class QualityWarning(BaseModel):
    code: str
    title: str
    message: str
    severity: str = Field(description="'info', 'warning', or 'critical'")
    affected_records: int = 0


class AnswerLengthStats(BaseModel):
    min_chars: int
    max_chars: int
    avg_chars: float
    median_chars: float
    min_words: int
    max_words: int
    avg_words: float
    median_words: float
    short_answers_count: int
    long_answers_count: int


class WorkerParticipationStats(BaseModel):
    min_answers: int
    max_answers: int
    avg_answers: float
    median_answers: float
    distribution_buckets: List[HistogramBucket]
    top_contributors: List[WorkerContribution]


class TaskCoverageStats(BaseModel):
    min_answers_per_task: int
    max_answers_per_task: int
    avg_answers_per_task: float
    coverage_buckets: List[HistogramBucket]


class SubmissionTimeStats(BaseModel):
    timestamps_present_count: int
    timestamps_missing_count: int
    timestamp_coverage_pct: float
    hourly_distribution: Dict[str, int]
    avg_seconds_spent: Optional[float] = None
    median_seconds_spent: Optional[float] = None


class DatasetQualityResponse(BaseModel):
    audit_id: str
    dataset_name: str
    total_records: int
    unique_workers: int
    unique_tasks: int
    completeness_score: float
    empty_answers_count: int
    missing_worker_ids_count: int
    missing_timestamps_count: int
    duplicate_task_submissions_count: int
    duplicate_submissions_count: int
    length_stats: AnswerLengthStats
    length_distribution: List[HistogramBucket]
    worker_participation: WorkerParticipationStats
    task_coverage: TaskCoverageStats
    submission_time_analysis: SubmissionTimeStats
    warnings: List[QualityWarning]
    disclaimer: str = (
        "Dataset quality analytics evaluate completeness, answer length distributions, "
        "and submission hygiene. Quality anomalies are descriptive and do not constitute "
        "evidence of AI generation or worker misconduct."
    )
