import statistics
from collections import Counter
from typing import List

from app.models.audit import Audit, AuditAnswer
from app.schemas.quality import (
    AnswerLengthStats,
    DatasetQualityResponse,
    HistogramBucket,
    QualityWarning,
    SubmissionTimeStats,
    TaskCoverageStats,
    WorkerContribution,
    WorkerParticipationStats,
)


def compute_dataset_quality_profile(
    audit: Audit,
    answers: List[AuditAnswer],
) -> DatasetQualityResponse:
    """Computes comprehensive descriptive dataset hygiene and completeness analytics

    from the set of audit answer records.

    Philosophical Invariant:
    Dataset quality metrics represent data hygiene and completeness. They are strictly
    separated from contamination findings and must never be interpreted as verdicts
    of AI generation or worker cheating.
    """
    total_records = len(answers)
    if total_records == 0:
        return _empty_quality_response(audit)

    # 1. Base entities and completeness
    worker_ids = [a.worker_id.strip() for a in answers if a.worker_id and a.worker_id.strip()]
    task_ids = [a.task_id.strip() for a in answers if a.task_id and a.task_id.strip()]

    unique_workers = len(set(worker_ids))
    unique_tasks = len(set(task_ids))

    missing_worker_ids = sum(1 for a in answers if not a.worker_id or not a.worker_id.strip())
    empty_answers = sum(1 for a in answers if not a.answer or not a.answer.strip())

    # Timestamps
    records_with_timestamp = sum(1 for a in answers if a.submitted_at is not None)
    missing_timestamps = total_records - records_with_timestamp
    timestamp_coverage_pct = round((records_with_timestamp / total_records) * 100, 2)

    # Duplicate tasks
    task_counts = Counter(a.task_id for a in answers if a.task_id)
    dup_task_submissions = sum(count - 1 for count in task_counts.values() if count > 1)

    # Exact duplicate answers (normalized lower stripped)
    clean_answer_texts = [
        a.answer.strip().lower() for a in answers if a.answer and a.answer.strip()
    ]
    answer_text_counts = Counter(clean_answer_texts)
    duplicate_submissions = sum(c - 1 for c in answer_text_counts.values() if c > 1)

    # Completeness score (0-100)
    # Weights: non-empty answer (40%), valid worker_id (25%), valid task_id (25%), timestamp (10%)
    non_empty_pct = ((total_records - empty_answers) / total_records) * 40.0
    valid_worker_pct = ((total_records - missing_worker_ids) / total_records) * 25.0
    valid_task_pct = (len(task_ids) / total_records) * 25.0
    timestamp_pct = (records_with_timestamp / total_records) * 10.0
    completeness_score = round(non_empty_pct + valid_worker_pct + valid_task_pct + timestamp_pct, 1)

    # 2. Answer length statistics
    char_lengths: List[int] = [len(a.answer) for a in answers if a.answer]
    word_lengths: List[int] = [len(a.answer.split()) for a in answers if a.answer]

    if not char_lengths:
        char_lengths = [0]
    if not word_lengths:
        word_lengths = [0]

    min_chars = min(char_lengths)
    max_chars = max(char_lengths)
    avg_chars = round(statistics.mean(char_lengths), 1)
    median_chars = round(float(statistics.median(char_lengths)), 1)

    min_words = min(word_lengths)
    max_words = max(word_lengths)
    avg_words = round(statistics.mean(word_lengths), 1)
    median_words = round(float(statistics.median(word_lengths)), 1)

    short_answers_count = sum(1 for c in char_lengths if c < 20)
    long_answers_count = sum(1 for c in char_lengths if c > 1000)

    length_stats = AnswerLengthStats(
        min_chars=min_chars,
        max_chars=max_chars,
        avg_chars=avg_chars,
        median_chars=median_chars,
        min_words=min_words,
        max_words=max_words,
        avg_words=avg_words,
        median_words=median_words,
        short_answers_count=short_answers_count,
        long_answers_count=long_answers_count,
    )

    # 3. Answer Length Distribution Histogram
    len_bins = [
        ("0-50", 0, 50),
        ("51-150", 51, 150),
        ("151-300", 151, 300),
        ("301-600", 301, 600),
        ("601-1200", 601, 1200),
        ("1200+", 1201, None),
    ]
    length_distribution: List[HistogramBucket] = []
    for label, b_min, b_max in len_bins:
        if b_max is not None:
            c = sum(1 for ch_len in char_lengths if b_min <= ch_len <= b_max)
        else:
            c = sum(1 for ch_len in char_lengths if ch_len >= b_min)
        pct = round((c / total_records) * 100, 1)
        length_distribution.append(
            HistogramBucket(
                bucket=label,
                min_val=b_min,
                max_val=b_max,
                count=c,
                percentage=pct,
            )
        )

    # 4. Worker Participation Distribution
    worker_answer_counts = Counter(worker_ids)
    w_counts_list = list(worker_answer_counts.values()) or [0]

    min_w = min(w_counts_list)
    max_w = max(w_counts_list)
    avg_w = round(statistics.mean(w_counts_list), 1)
    median_w = round(float(statistics.median(w_counts_list)), 1)

    w_bins = [
        ("1 answer", 1, 1),
        ("2-5 answers", 2, 5),
        ("6-10 answers", 6, 10),
        ("11-20 answers", 11, 20),
        ("20+ answers", 21, None),
    ]
    w_distribution: List[HistogramBucket] = []
    total_workers_counted = len(w_counts_list)
    for label, b_min, b_max in w_bins:
        if b_max is not None:
            c = sum(1 for count in w_counts_list if b_min <= count <= b_max)
        else:
            c = sum(1 for count in w_counts_list if count >= b_min)
        pct = round((c / total_workers_counted) * 100, 1) if total_workers_counted else 0.0
        w_distribution.append(
            HistogramBucket(
                bucket=label,
                min_val=b_min,
                max_val=b_max,
                count=c,
                percentage=pct,
            )
        )

    # Top contributors
    top_contributors = [
        WorkerContribution(
            worker_id=wid,
            answer_count=cnt,
            percentage_of_total=round((cnt / total_records) * 100, 1),
        )
        for wid, cnt in worker_answer_counts.most_common(10)
    ]

    worker_participation = WorkerParticipationStats(
        min_answers=min_w,
        max_answers=max_w,
        avg_answers=avg_w,
        median_answers=median_w,
        distribution_buckets=w_distribution,
        top_contributors=top_contributors,
    )

    # 5. Task Coverage
    t_counts_list = list(task_counts.values()) or [0]
    min_t = min(t_counts_list)
    max_t = max(t_counts_list)
    avg_t = round(statistics.mean(t_counts_list), 1)

    t_bins = [
        ("1 answer", 1, 1),
        ("2-3 answers", 2, 3),
        ("4-5 answers", 4, 5),
        ("6-10 answers", 6, 10),
        ("10+ answers", 11, None),
    ]
    t_distribution: List[HistogramBucket] = []
    total_tasks_counted = len(t_counts_list)
    for label, b_min, b_max in t_bins:
        if b_max is not None:
            c = sum(1 for count in t_counts_list if b_min <= count <= b_max)
        else:
            c = sum(1 for count in t_counts_list if count >= b_min)
        pct = round((c / total_tasks_counted) * 100, 1) if total_tasks_counted else 0.0
        t_distribution.append(
            HistogramBucket(
                bucket=label,
                min_val=b_min,
                max_val=b_max,
                count=c,
                percentage=pct,
            )
        )

    task_coverage = TaskCoverageStats(
        min_answers_per_task=min_t,
        max_answers_per_task=max_t,
        avg_answers_per_task=avg_t,
        coverage_buckets=t_distribution,
    )

    # 6. Submission-Time Analysis
    hourly_counts = {f"{h:02d}:00": 0 for h in range(24)}
    seconds_list: List[float] = []

    for a in answers:
        if a.submitted_at:
            h_key = f"{a.submitted_at.hour:02d}:00"
            hourly_counts[h_key] = hourly_counts.get(h_key, 0) + 1
        if a.seconds_spent is not None and a.seconds_spent > 0:
            seconds_list.append(float(a.seconds_spent))

    avg_sec = round(statistics.mean(seconds_list), 1) if seconds_list else None
    med_sec = round(float(statistics.median(seconds_list)), 1) if seconds_list else None

    submission_time_stats = SubmissionTimeStats(
        timestamps_present_count=records_with_timestamp,
        timestamps_missing_count=missing_timestamps,
        timestamp_coverage_pct=timestamp_coverage_pct,
        hourly_distribution=hourly_counts,
        avg_seconds_spent=avg_sec,
        median_seconds_spent=med_sec,
    )

    # 7. Quality Warnings
    warnings: List[QualityWarning] = []

    if empty_answers > 0:
        warnings.append(
            QualityWarning(
                code="EMPTY_ANSWERS",
                title="Empty or Blank Answers Detected",
                message=f"{empty_answers} records contain no answer text or only whitespace.",
                severity="critical" if empty_answers > 5 else "warning",
                affected_records=empty_answers,
            )
        )

    if missing_timestamps > (total_records * 0.25):
        warnings.append(
            QualityWarning(
                code="MISSING_TIMESTAMPS",
                title="Low Timestamp Coverage",
                message=(
                    f"{missing_timestamps} records ({100 - timestamp_coverage_pct:.1f}%) "
                    "lack submission timestamps, preventing velocity profiling."
                ),
                severity="warning",
                affected_records=missing_timestamps,
            )
        )

    if missing_worker_ids > 0:
        warnings.append(
            QualityWarning(
                code="MISSING_WORKER_IDS",
                title="Missing Worker Identifiers",
                message=f"{missing_worker_ids} submissions lack an identifiable worker ID.",
                severity="warning",
                affected_records=missing_worker_ids,
            )
        )

    # Worker concentration warning (>35% of total dataset by 1 worker in datasets with >15 answers)
    if top_contributors and total_records >= 15:
        top_w = top_contributors[0]
        if top_w.percentage_of_total > 35.0:
            warnings.append(
                QualityWarning(
                    code="HIGH_WORKER_CONCENTRATION",
                    title="High Single-Worker Contribution",
                    message=(
                        f"Worker '{top_w.worker_id}' contributed {top_w.percentage_of_total}% "
                        f"({top_w.answer_count} records) of the entire dataset."
                    ),
                    severity="info",
                    affected_records=top_w.answer_count,
                )
            )

    if short_answers_count > (total_records * 0.20) and total_records >= 10:
        warnings.append(
            QualityWarning(
                code="HIGH_SHORT_ANSWERS",
                title="High Proportion of Short Answers",
                message=(
                    f"{short_answers_count} answers are fewer than 20 characters "
                    f"({round((short_answers_count / total_records) * 100, 1)}%)."
                ),
                severity="info",
                affected_records=short_answers_count,
            )
        )

    if duplicate_submissions > (total_records * 0.15) and total_records >= 10:
        warnings.append(
            QualityWarning(
                code="EXACT_DUPLICATE_ANSWERS",
                title="Exact Duplicate Submissions",
                message=(
                    f"{duplicate_submissions} answers share verbatim identical text with another "
                    "record in this dataset."
                ),
                severity="warning",
                affected_records=duplicate_submissions,
            )
        )

    return DatasetQualityResponse(
        audit_id=audit.id,
        dataset_name=audit.dataset_name or "dataset.csv",
        total_records=total_records,
        unique_workers=unique_workers,
        unique_tasks=unique_tasks,
        completeness_score=completeness_score,
        empty_answers_count=empty_answers,
        missing_worker_ids_count=missing_worker_ids,
        missing_timestamps_count=missing_timestamps,
        duplicate_task_submissions_count=dup_task_submissions,
        duplicate_submissions_count=duplicate_submissions,
        length_stats=length_stats,
        length_distribution=length_distribution,
        worker_participation=worker_participation,
        task_coverage=task_coverage,
        submission_time_analysis=submission_time_stats,
        warnings=warnings,
    )


def _empty_quality_response(audit: Audit) -> DatasetQualityResponse:
    """Fallback response for audits with 0 uploaded records."""
    return DatasetQualityResponse(
        audit_id=audit.id,
        dataset_name=audit.dataset_name or "dataset.csv",
        total_records=0,
        unique_workers=0,
        unique_tasks=0,
        completeness_score=0.0,
        empty_answers_count=0,
        missing_worker_ids_count=0,
        missing_timestamps_count=0,
        duplicate_task_submissions_count=0,
        duplicate_submissions_count=0,
        length_stats=AnswerLengthStats(
            min_chars=0,
            max_chars=0,
            avg_chars=0.0,
            median_chars=0.0,
            min_words=0,
            max_words=0,
            avg_words=0.0,
            median_words=0.0,
            short_answers_count=0,
            long_answers_count=0,
        ),
        length_distribution=[],
        worker_participation=WorkerParticipationStats(
            min_answers=0,
            max_answers=0,
            avg_answers=0.0,
            median_answers=0.0,
            distribution_buckets=[],
            top_contributors=[],
        ),
        task_coverage=TaskCoverageStats(
            min_answers_per_task=0,
            max_answers_per_task=0,
            avg_answers_per_task=0.0,
            coverage_buckets=[],
        ),
        submission_time_analysis=SubmissionTimeStats(
            timestamps_present_count=0,
            timestamps_missing_count=0,
            timestamp_coverage_pct=0.0,
            hourly_distribution={f"{h:02d}:00": 0 for h in range(24)},
            avg_seconds_spent=None,
            median_seconds_spent=None,
        ),
        warnings=[
            QualityWarning(
                code="EMPTY_DATASET",
                title="Dataset Has Zero Records",
                message="No records found in this audit for quality profiling.",
                severity="warning",
                affected_records=0,
            )
        ],
    )
