import json
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.core.security import sanitize_filename
from app.schemas.dataset import DatasetValidationResponse
from app.services.dataset import validate_and_parse_dataset

router = APIRouter(prefix="/audits", tags=["Audits"])


@router.post("/validate", response_model=DatasetValidationResponse)
async def validate_dataset_endpoint(
    file: UploadFile = File(...),
    column_mapping: Optional[str] = Form(None),
):
    """
    Validates uploaded CSV or JSONL dataset against requirements FR-1 through FR-8.
    Does not persist the audit or answers to the database.
    """
    custom_map = None
    if column_mapping:
        try:
            custom_map = json.loads(column_mapping)
        except Exception:
            pass

    safe_name = sanitize_filename(file.filename or "dataset.csv")
    content = await file.read()

    validation_resp, _ = validate_and_parse_dataset(
        content_bytes=content,
        filename=safe_name,
        custom_mapping=custom_map,
    )

    return validation_resp
