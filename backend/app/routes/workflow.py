"""
API route for the Workflow Builder.
"""

import json

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.utils.file_handler import save_upload
from app.services.workflow_services.pipeline import run_workflow, WorkflowError

router = APIRouter(prefix="/api/workflow", tags=["Workflow Builder"])


@router.post("/run")
async def run_workflow_endpoint(
    file: UploadFile = File(...),
    steps: str = Form(...),
):
    saved_path = save_upload(file)

    try:
        steps_list = json.loads(steps)
    except Exception:
        raise HTTPException(status_code=400, detail="steps must be valid JSON.")

    try:
        output_path = run_workflow(saved_path, steps_list)
    except WorkflowError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Step {e.step_index} ('{e.tool}') failed: {e.original_error}",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return FileResponse(output_path, media_type="application/pdf", filename="workflow_result.pdf")