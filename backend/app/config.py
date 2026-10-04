"""
Central configuration for the KaagazAI backend.
Reads settings from environment variables (.env file) so nothing
sensitive or environment- specific is hard=coded.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is not installed, assume environment variables are set elsewhere

# ---- Genral settings -----
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 25))
FILE_RETENTION_MINUTES = int(os.getenv("FILE_RETENTION_MINUTES", 60))

# --- AI provider settings (used later by report_generator / visualizer) ---
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp_files"
TEMP_DIR.mkdir(exist_ok=True)

# --- CORS (frontend origin allowed to call this backend) ---
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")