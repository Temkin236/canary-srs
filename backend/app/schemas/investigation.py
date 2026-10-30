import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FindingReviewUpdateRequest(BaseModel):
    review_status: str = Field(
        ...,
        pattern="^(pending_review|under_review|reviewed|dismissed|needs_investigation)$",
        description="Updated human review adjudication status",
    )
    reviewer_notes: Optional[str] = None
    assigned_reviewer: Optional[str] = None
    dismissal_reason: Optional[str] = None
    reviewer_id: str = Field(default="reviewer", description="Identifier of the reviewer")


class FindingReviewHistoryItem(BaseModel):
    id: str
    finding_id: str
    action: str
    previous_status: str
    new_status: str
    reviewer_id: str
    notes: Optional[str] = None
    dismissal_reason: Optional[str] = None
    created_at: datetime.datetime


class FindingDetailedItem(BaseModel):
    id: str
    audit_id: str
    answer_id: str
    task_id: str
    worker_id: str
    check_identifier: str
    finding_type: str
    evidence_confidence: str
    explanation: str
    evidence_text: Optional[str] = None
    evidence_offsets: Optional[List[int]] = None
    numerical_measurements: Dict[str, Any] = {}
    related_answer_ids: List[str] = []
    limitations: str
    review_status: str
    reviewer_notes: Optional[str] = None
    assigned_reviewer: Optional[str] = None
    reviewed_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    worker_answer: Optional[str] = None
    prompt: Optional[str] = None
    history: List[FindingReviewHistoryItem] = []


class ComparisonDiffSegment(BaseModel):
    text: str
    is_match: bool = False
    is_source_only: bool = False
    is_target_only: bool = False


class SideBySideComparisonResponse(BaseModel):
    finding_id: str
    task_id: str
    worker_id: str
    comparison_type: str
    source_answer: str
    target_answer: str
    target_label: str
    similarity_score: Optional[float] = None
    measurements: Dict[str, Any] = {}
    explanation: str
    diff_segments: List[ComparisonDiffSegment]
    limitations: str


class MarkerInvestigationItem(BaseModel):
    id: str
    task_id: str
    marker_id: str
    expected_marker: str
    detected: bool
    detected_marker: Optional[str] = None
    location_in_answer: Optional[List[int]] = None
    preparation_version: str = "v1.0"
    finding_id: Optional[str] = None


class DuplicateClusterItem(BaseModel):
    cluster_id: str
    task_id: str
    worker_ids: List[str]
    answer_ids: List[str]
    representative_text: str
    similarity_matrix: Dict[str, float]
    findings_count: int


class InvestigationWorkspaceResponse(BaseModel):
    audit: Dict[str, Any]
    findings: List[FindingDetailedItem]
    markers: List[MarkerInvestigationItem]
    duplicate_clusters: List[DuplicateClusterItem]
    calibration: Optional[Dict[str, Any]] = None
