import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


def get_utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class Audit(Base):
    __tablename__ = "audits"

    id = Column(String(36), primary_key=True, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    status = Column(String(32), default="queued", nullable=False, index=True)
    answers_count = Column(Integer, default=0, nullable=False)
    workers_count = Column(Integer, default=0, nullable=False)
    flagged_workers_count = Column(Integer, default=0, nullable=False)
    consent_external_ai = Column(Boolean, default=False, nullable=False)
    config = Column(JSON, default=dict, nullable=False)
    summary_metrics = Column(JSON, default=dict, nullable=False)
    dataset_name = Column(String(256), default="dataset.csv", nullable=False)
    owner_id = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)

    # Relationships
    answers = relationship("AuditAnswer", back_populates="audit", cascade="all, delete-orphan")
    reference_answers = relationship(
        "ReferenceAnswer", back_populates="audit", cascade="all, delete-orphan"
    )
    markers = relationship("Marker", back_populates="audit", cascade="all, delete-orphan")
    check_results = relationship(
        "CheckResult", back_populates="audit", cascade="all, delete-orphan"
    )
    findings = relationship("Finding", back_populates="audit", cascade="all, delete-orphan")
    calibration_run = relationship(
        "CalibrationRun", back_populates="audit", uselist=False, cascade="all, delete-orphan"
    )
    job_state = relationship(
        "JobState", back_populates="audit", uselist=False, cascade="all, delete-orphan"
    )


class AuditAnswer(Base):
    __tablename__ = "audit_answers"

    id = Column(String(36), primary_key=True, index=True)
    audit_id = Column(
        String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id = Column(String(128), nullable=False, index=True)
    worker_id = Column(String(128), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    seconds_spent = Column(Float, nullable=True)

    audit = relationship("Audit", back_populates="answers")
    findings = relationship("Finding", back_populates="audit_answer", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_audit_task_worker", "audit_id", "task_id", "worker_id"),)


class ReferenceAnswer(Base):
    __tablename__ = "reference_answers"

    id = Column(String(36), primary_key=True, index=True)
    audit_id = Column(
        String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id = Column(String(128), nullable=False, index=True)
    provider = Column(String(64), nullable=False)  # e.g., gemini, offline-synthetic
    model_name = Column(String(128), nullable=False)
    reference_text = Column(Text, nullable=False)
    generation_settings = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    audit = relationship("Audit", back_populates="reference_answers")


class Marker(Base):
    __tablename__ = "markers"

    id = Column(String(36), primary_key=True, index=True)
    audit_id = Column(
        String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=True, index=True
    )
    task_id = Column(String(128), nullable=False, index=True)
    marker_token = Column(String(128), nullable=False, index=True)
    hiding_method = Column(String(64), nullable=False)  # zero_width, prompt_embedded
    prompt_template = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    audit = relationship("Audit", back_populates="markers")


class CheckResult(Base):
    __tablename__ = "check_results"

    id = Column(String(36), primary_key=True, index=True)
    audit_id = Column(
        String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    check_name = Column(String(64), nullable=False)  # marker, similarity, duplicates, speed
    status = Column(
        String(32), default="pending", nullable=False
    )  # pending, running, completed, skipped, failed
    execution_time_ms = Column(Integer, default=0, nullable=False)
    findings_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)

    audit = relationship("Audit", back_populates="check_results")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, index=True)
    audit_id = Column(
        String(36), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    answer_id = Column(
        String(36), ForeignKey("audit_answers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id = Column(String(128), nullable=False, index=True)
    worker_id = Column(String(128), nullable=False, index=True)
    check_identifier = Column(String(64), nullable=False, index=True)
    finding_type = Column(String(64), nullable=False)
    evidence_confidence = Column(String(16), nullable=False, index=True)  # High, Medium, Low
    explanation = Column(Text, nullable=False)
    evidence_text = Column(Text, nullable=True)
    evidence_offsets = Column(JSON, nullable=True)  # [start, end]
    numerical_measurements = Column(JSON, default=dict, nullable=False)
    related_answer_ids = Column(JSON, default=list, nullable=False)
    limitations = Column(
        Text,
        default="Evidence for human review only; does not prove cheating.",
        nullable=False,
    )
    review_status = Column(String(32), default="pending_review", nullable=False, index=True)
    reviewer_notes = Column(Text, nullable=True)
    assigned_reviewer = Column(String(128), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    audit = relationship("Audit", back_populates="findings")
    audit_answer = relationship("AuditAnswer", back_populates="findings")


class CalibrationRun(Base):
    __tablename__ = "calibration_runs"

    id = Column(String(36), primary_key=True, index=True)
    audit_id = Column(
        String(36),
        ForeignKey("audits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    sample_size = Column(Integer, nullable=False)
    flagged_count = Column(Integer, nullable=False)
    estimated_fp_rate = Column(Float, nullable=False)
    ci_lower = Column(Float, nullable=False)
    ci_upper = Column(Float, nullable=False)
    ci_method = Column(String(32), default="wilson", nullable=False)
    insufficient_data_reason = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    audit = relationship("Audit", back_populates="calibration_run")


class JobState(Base):
    __tablename__ = "job_states"

    id = Column(String(36), primary_key=True, index=True)
    audit_id = Column(
        String(36),
        ForeignKey("audits.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    stage = Column(String(32), default="queued", nullable=False)
    progress_percentage = Column(Integer, default=0, nullable=False)
    current_check = Column(String(64), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    started_at = Column(DateTime, nullable=True)
    last_heartbeat = Column(DateTime, default=get_utc_now, nullable=False)
    error_log = Column(Text, nullable=True)

    audit = relationship("Audit", back_populates="job_state")


class EvaluationMetadata(Base):
    __tablename__ = "evaluation_metadata"

    id = Column(String(36), primary_key=True, index=True)
    dataset_version = Column(String(64), nullable=False)
    sample_size = Column(Integer, nullable=False)
    true_positives = Column(Integer, nullable=False)
    false_positives = Column(Integer, nullable=False)
    true_negatives = Column(Integer, nullable=False)
    false_negatives = Column(Integer, nullable=False)
    tpr = Column(Float, nullable=False)
    fpr = Column(Float, nullable=False)
    tpr_ci_lower = Column(Float, nullable=False)
    tpr_ci_upper = Column(Float, nullable=False)
    fpr_ci_lower = Column(Float, nullable=False)
    fpr_ci_upper = Column(Float, nullable=False)
    ci_method = Column(String(32), default="wilson", nullable=False)
    configuration = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
