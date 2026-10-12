
@echo off
title Kaagaz AI Launcher

echo ========================================
echo       Starting Kaagaz AI
echo ========================================

REM Start Backend
start "Kaagaz AI Backend" /D "C:\Users\hp\Documents\Kaagaz AI\backend" cmd /k "set PATH=C:\msys64\ucrt64\bin;%PATH% && set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\ucrt64\bin && venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 5 /nobreak >nul

REM Start Frontend
start "Kaagaz AI Frontend" /D "C:\Users\hp\Documents\Kaagaz AI\KaagazAI-frontend\frontend" cmd /k "npm.cmd run dev -- --host 127.0.0.1"

echo.
echo Waiting for frontend to start...
timeout /t 8 /nobreak >nul

REM Open Backend API Docs
start "" "http://127.0.0.1:8000/docs"

echo.
echo Check the Frontend terminal for its exact URL.
echo Open that URL in your browser.
echo.
pause
