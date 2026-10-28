
@echo off
title Kaagaz AI Launcher

echo Starting Kaagaz AI Backend...

start "Kaagaz AI Backend" cmd /k "cd /d ""C:\Users\hp\Documents\Kaagaz AI\backend"" && set ""PATH=C:\msys64\ucrt64\bin;%PATH%"" && set ""WEASYPRINT_DLL_DIRECTORIES=C:\msys64\ucrt64\bin"" && venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Kaagaz AI Frontend...

start "Kaagaz AI Frontend" cmd /k "cd /d ""C:\Users\hp\Documents\Kaagaz AI\KaagazAI-frontend\frontend"" && npm.cmd run dev"

echo.
echo Both servers are starting.
echo Backend: http://127.0.0.1:8000/docs
echo Frontend: http://localhost:5173/
pause
