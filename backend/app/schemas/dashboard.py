import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    total_audits: int
    completed_audits: int
    running_audits: int
    failed_audits: int
    total_answers_analyzed: int
    findings_requiring_review: int
    reviewed_findings: int
    high_confidence_findings: int
    medium_confidence_findings: int
    low_confidence_findings: int
    findings_by_category: Dict[str, int]
    audits_by_status: Dict[str, int]
    activity_over_time: List[Dict[str, Any]]
    dataset_size_distribution: Dict[str, int]


class DashboardAuditItem(BaseModel):
    id: str
    dataset_name: str
    status: str
    answers_count: int
    workers_count: int
    flagged_workers_count: int
    findings_count: int
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    duration_seconds: Optional[float] = None
    expires_at: datetime.datetime
    owner_id: Optional[str] = None


class DashboardAuditsResponse(BaseModel):
    items: List[DashboardAuditItem]
    total: int
    page: int
    page_size: int
    total_pages: int
