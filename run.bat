@echo off
echo ========================================================
echo Starting PDS Log Intelligence Platform...
echo ========================================================
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
