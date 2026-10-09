"""
Workflow Builder — runs a user-defined sequence of PDF operations on a
single file, where each step's output becomes the next step's input.
"""

from pathlib import Path
from typing import Any, Dict, List

from app.services.pdf_service.rotate import rotate_pdf
from app.services.pdf_service.delete_page import delete_pages
from app.services.pdf_service.compress import compress_pdf
from app.services.pdf_service.watermark import add_watermark
from app.services.pdf_service.remove_blank import remove_blank_pages
from app.services.pdf_service.extract_pages import extract_pages
from app.services.pdf_service.reorder_pages import reorder_pages
from app.services.pdf_service.crop import crop_pdf
from app.services.pdf_service.page_numbers import add_page_numbers


class WorkflowError(Exception):
    def __init__(self, step_index: int, tool: str, original_error: str):
        self.step_index = step_index
        self.tool = tool
        self.original_error = original_error
        super().__init__(f"Step {step_index} ('{tool}') failed: {original_error}")


def _run_rotate(path, params):
    return rotate_pdf(path, params["angle"], params.get("pages"))

def _run_delete_pages(path, params):
    return delete_pages(path, params["pages"])

def _run_compress(path, params):
    return compress_pdf(path, params.get("quality", "medium"))

def _run_watermark(path, params):
    return add_watermark(path, params.get("text", "CONFIDENTIAL"))

def _run_remove_blank(path, params):
    output_path, _removed = remove_blank_pages(path)
    return output_path

def _run_extract_pages(path, params):
    return extract_pages(path, params["pages"])

def _run_reorder_pages(path, params):
    return reorder_pages(path, params["new_order"])

def _run_crop(path, params):
    return crop_pdf(path, params.get("left", 0), params.get("bottom", 0),
                     params.get("right", 0), params.get("top", 0))

def _run_add_page_numbers(path, params):
    return add_page_numbers(path, params.get("position", "bottom-center"))


TOOL_REGISTRY = {
    "rotate": _run_rotate,
    "delete_pages": _run_delete_pages,
    "compress": _run_compress,
    "watermark": _run_watermark,
    "remove_blank_pages": _run_remove_blank,
    "extract_pages": _run_extract_pages,
    "reorder_pages": _run_reorder_pages,
    "crop": _run_crop,
    "add_page_numbers": _run_add_page_numbers,
}


def run_workflow(input_path: Path, steps: List[Dict[str, Any]]) -> Path:
    if not steps:
        raise ValueError("Workflow must contain at least one step.")

    current_path = input_path

    for i, step in enumerate(steps, start=1):
        tool_name = step.get("tool")
        params = step.get("params", {})

        if tool_name not in TOOL_REGISTRY:
            raise WorkflowError(i, tool_name, f"Unknown tool '{tool_name}'. "
                                 f"Available: {list(TOOL_REGISTRY.keys())}")

        tool_function = TOOL_REGISTRY[tool_name]
        try:
            current_path = tool_function(current_path, params)
        except Exception as e:
            raise WorkflowError(i, tool_name, str(e))

    return current_path