"""
KaagazAI Backend — main entry point.

Run with:
    uvicorn app.main:app --reload
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGIN, FILE_RETENTION_MINUTES
from app.utils.file_handler import cleanup_old_files
from app.routes import pdf_tools, convert_tools, workflow,page_manager_routes


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_tools.router)
app.include_router(convert_tools.router)
app.include_router(workflow.router)
app.include_router(page_manager_routes.router)



@app.get("/")
async def root():
    return {"message": "KaagazAI backend is running."}


@app.get("/health")
async def health_check():
    return {"status": "ok"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    ...