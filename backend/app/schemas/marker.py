from typing import List, Optional

from pydantic import BaseModel, Field


class TaskInput(BaseModel):
    task_id: str
    prompt: str


class MarkerPrepareRequest(BaseModel):
    tasks: List[TaskInput]
    hiding_method: str = Field(default="zero_width", description="zero_width | prompt_embedded")


class PreparedTaskOutput(BaseModel):
    task_id: str
    prompt: str
    marker: str
    hiding_method: str
    prepared_prompt: str
    visible_preview: str
    model_received_preview: str


class ManifestItem(BaseModel):
    task_id: str
    marker: str
    hiding_method: str
    prompt: Optional[str] = None


class MarkerManifestSchema(BaseModel):
    format_version: str = "1.0"
    created_at: str
    items: List[ManifestItem]


class MarkerPrepareResponse(BaseModel):
    tasks: List[PreparedTaskOutput]
    manifest: MarkerManifestSchema
