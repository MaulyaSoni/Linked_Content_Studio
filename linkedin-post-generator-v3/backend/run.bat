@echo off
echo Starting LinkedIn Post Generator v3.0 Backend...
cd /d %~dp0
pip install -q fastapi uvicorn pydantic python-dotenv sqlalchemy httpx
echo.
echo Starting server on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --port 8000
