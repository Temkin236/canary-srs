from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RowError(BaseModel):
    row: Optional[int] = None
    field: Optional[str] = None
    message: str


class RowWarning(BaseModel):
    row: Optional[int] = None
    field: Optional[str] = None
    message: str


class DatasetValidationResponse(BaseModel):
    valid: bool
    total_rows: int
    tasks_count: int
    workers_count: int
    detected_columns: List[str]
    column_mapping_used: Dict[str, str]
    errors: List[RowError] = Field(default_factory=list)
    warnings: List[RowWarning] = Field(default_factory=list)
    preview: List[Dict[str, Any]] = Field(default_factory=list)


class ColumnMappingRequest(BaseModel):
    task_id_col: Optional[str] = None
    prompt_col: Optional[str] = None
    worker_id_col: Optional[str] = None
    answer_col: Optional[str] = None
    submitted_at_col: Optional[str] = None
    seconds_spent_col: Optional[str] = None
