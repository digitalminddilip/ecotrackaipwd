@echo off
echo Starting EcoTrack AI FastAPI on port 8000...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
