@echo off
title OpenJarvis Unified Launcher (Backend + Frontend)
setlocal enabledelayedexpansion

cd /d J:\tasksorobon\jarvis
set PYTHONPATH=J:\tasksorobon\jarvis\src

echo.
echo =========================================
echo  JARVIS STARTUP SEQUENCE
echo =========================================
echo.

REM Step 1: Doctor validation
echo [1/4] Running Doctor Jarvis validation...
.\\.venv\Scripts\python -m openjarvis.cli doctor
if errorlevel 1 (
    echo ERROR: Doctor validation failed. Aborting.
    pause
    exit /b 1
)
timeout /t 2 >nul

REM Step 2: Backend (FastAPI + ECC Agents + Chat Pipeline)
echo [2/4] Starting Backend (Port 8000)...
start "Jarvis Backend" .\\.venv\Scripts\python -m uvicorn openjarvis.server.main:app --reload --host 127.0.0.1 --port 8000
timeout /t 3 >nul

REM Step 3: Frontend (Vite + React)
echo [3/4] Starting Frontend (Port 5173)...
cd /d J:\tasksorobon\jarvis\frontend
start "Jarvis Frontend" cmd /k npm run dev -- --port 5173 --strictPort
timeout /t 3 >nul

REM Step 4: Open browser
echo [4/4] Opening browser to http://127.0.0.1:5173...
timeout /t 2 >nul
start http://127.0.0.1:5173

echo.
echo =========================================
echo  ✅ JARVIS ECOSYSTEM ONLINE
echo =========================================
echo.
echo Backend API:  http://127.0.0.1:8000/v1/health
echo Swagger Docs: http://127.0.0.1:8000/docs
echo Frontend:     http://127.0.0.1:5173
echo.
echo [Ctrl+C to stop services]
pause