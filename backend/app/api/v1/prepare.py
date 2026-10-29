import json

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.marker import MarkerManifestSchema, MarkerPrepareRequest, MarkerPrepareResponse
from app.services.marker_gen import (
    generate_marker_manifest,
    prepare_task_with_marker,
    validate_manifest,
)

router = APIRouter(prefix="/prepare", tags=["Prepare"])


@router.post("/markers", response_model=MarkerPrepareResponse)
def prepare_markers_endpoint(request: MarkerPrepareRequest):
    """
    Generates cryptographically random canary markers and prepared prompt templates.
    Supports 'zero_width' and 'prompt_embedded' hiding methods.
    """
    if not request.tasks:
        raise HTTPException(status_code=400, detail="At least one task is required.")

    prepared_tasks = [
        prepare_task_with_marker(task, hiding_method=request.hiding_method)
        for task in request.tasks
    ]

    manifest = generate_marker_manifest(prepared_tasks)
    return MarkerPrepareResponse(tasks=prepared_tasks, manifest=manifest)


@router.post("/export", response_model=MarkerManifestSchema)
def export_manifest_endpoint(manifest: MarkerManifestSchema):
    """Echoes and validates a marker manifest for client download."""
    return manifest


@router.post("/import", response_model=MarkerManifestSchema)
async def import_manifest_endpoint(file: UploadFile = File(...)):
    """Imports and validates an existing marker manifest JSON file."""
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON manifest file: {str(e)}")

    valid, err = validate_manifest(data)
    if not valid:
        raise HTTPException(status_code=400, detail=f"Invalid manifest format: {err}")

    return MarkerManifestSchema(**data)
