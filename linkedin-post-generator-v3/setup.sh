#!/bin/bash

# LinkedIn Post Generator v3.0 - Setup Script
# This script sets up the entire project

echo "🚀 Setting up LinkedIn Post Generator v3.0..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Prerequisites met!"

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your API keys"
fi

cd ..

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend..."
cd frontend

# Install dependencies
npm install

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit backend/.env with your API keys (GROQ_API_KEY, OPENAI_API_KEY, etc.)"
echo "2. Start PostgreSQL and Redis"
echo "3. Run backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "4. Run frontend: cd frontend && npm run dev"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Happy building! 🎉"
