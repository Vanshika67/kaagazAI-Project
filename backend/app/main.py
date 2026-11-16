"""
KaagazAI Backend â€” main entry point.

Run with:
    uvicorn app.main:app --reload
"""

import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import FILE_RETENTION_MINUTES
from app.utils.file_handler import cleanup_old_files
from app.routes import pdf_tools, convert_tools, workflow, page_manager_routes
from app.routes import new_tools
from app.routes import office_tools
from app.routes import password_recovery
from app.routes import label_organize
from app.routes import resume_builder
from app.routes.extra_tools import router as extra_router
from app.routes.bulk_tools import router as bulk_router
from app.routes import handwriting
from app.routes import ai_draft


async def periodic_cleanup():
    """Background task: deletes old temp files every few minutes for privacy."""
    while True:
        cleanup_old_files()
        await asyncio.sleep(FILE_RETENTION_MINUTES * 60 / 2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodic_cleanup())
    yield
    task.cancel()


app = FastAPI(
    title="KaagazAI API",
    description="Backend for the KaagazAI PDF & document intelligence platform.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: localhost / 127.0.0.1 ke kisi bhi port se allow
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.exception_handler(Exception)
async def all_errors(request: Request, exc: Exception):
    """Har unhandled error ka traceback terminal mein print karta hai
    aur response mein error ka naam + message bhejta hai."""
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
    )


app.include_router(pdf_tools.router)
app.include_router(convert_tools.router)
app.include_router(workflow.router)
app.include_router(page_manager_routes.router)
app.include_router(new_tools.router, prefix="/api")
app.include_router(office_tools.router, prefix="/api")
app.include_router(password_recovery.router, prefix="/api")
app.include_router(label_organize.router, prefix="/api")
app.include_router(resume_builder.router, prefix="/api")
app.include_router(extra_router, prefix="/api")
app.include_router(bulk_router, prefix="/api")
app.include_router(handwriting.router, prefix="/api")
app.include_router(ai_draft.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "KaagazAI backend is running."}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
