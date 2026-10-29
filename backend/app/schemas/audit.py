from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AuditCreateResponse(BaseModel):
    audit_id: str
    secret_token: str = Field(
        ...,
        description=(
            "Raw 256-bit secret token. Never stored in DB; required to view/export results."
        ),
    )
    status: str
    expires_at: datetime
    answers_count: int


class AuditStatusResponse(BaseModel):
    audit_id: str
    status: str  # queued, running, completed, partially_completed, failed
    stage: str
    progress_percentage: int
    current_check: Optional[str] = None
    answers_count: int = 0
    workers_count: int = 0
    flagged_workers_count: int = 0
    expires_at: datetime
    summary_metrics: Dict[str, Any] = Field(default_factory=dict)
