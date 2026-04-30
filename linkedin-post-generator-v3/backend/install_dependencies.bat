@echo off
echo ========================================
echo Installing Backend Dependencies...
echo ========================================
echo.

cd /d %~dp0

echo Installing core dependencies...
pip install -q fastapi uvicorn pydantic python-dotenv sqlalchemy

echo Installing authentication packages...
pip install -q python-jose passlib[bcrypt] bcrypt==4.0.1 python-multipart

echo Installing AI/ML packages...
pip install -q langchain langchain-core langchain-groq langchain-openai langgraph

echo Installing HTTP clients...
pip install -q httpx requests

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the server, run:
echo   python -m uvicorn app.main:app --reload --port 8000
echo.
pause
