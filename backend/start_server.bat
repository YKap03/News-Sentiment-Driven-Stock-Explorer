@echo off
echo Starting FastAPI Backend Server...
echo.
cd /d %~dp0
python -m uvicorn app:app --reload
pause

