# LinkedIn Post Generator v3.0

AI-powered LinkedIn post generator with user profiling, fact-checking, and multi-modal content generation.

## Features

✅ **AI-Powered Generation** - LangGraph workflows with LLM orchestration
✅ **User Profiling** - Learns your unique writing style
✅ **Fact-Checking** - Multi-layer hallucination prevention
✅ **Image Generation** - AI-generated visuals for posts
✅ **Quality Scoring** - Automatic post quality assessment
✅ **Authentication** - Secure JWT-based auth
✅ **Analytics** - Track post performance and metrics
✅ **Modern UI** - Next.js 14 with TypeScript and TailwindCSS

## Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- Zustand (State Management)
- React Query
- Framer Motion

**Backend:**
- FastAPI
- LangChain + LangGraph
- PostgreSQL
- Redis
- Groq/OpenAI LLMs

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL
- Redis

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local  # if exists

# Run the frontend
npm run dev
```

### Using Docker

```bash
docker-compose up -d
```

## API Endpoints

- **Auth**: `/api/auth/register`, `/api/auth/login`
- **Posts**: `/api/posts/generate`, `/api/posts/history`
- **Images**: `/api/images/generate`
- **Users**: `/api/users/profile`, `/api/users/style`
- **Analytics**: `/api/analytics/overview`

## Environment Variables

### Backend (.env)
```
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:password@localhost:5432/linkedin_generator
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Documentation

- [Project Layout Guide](./docs/PROJECT_LAYOUT.md)
- [Backend Feature Reference](./docs/BACKEND_FEATURE_REFERENCE.md)
- [Tech Stack Revision](../legacy/shared/TECH_STACK_REVISION_v3.0.md)
- [Advanced Features](../legacy/shared/ADVANCED_FEATURES_IMPLEMENTATION.md)
- [Implementation Roadmap](../legacy/shared/COMPLETE_v3.0_IMPLEMENTATION_ROADMAP.txt)

## License

MIT
