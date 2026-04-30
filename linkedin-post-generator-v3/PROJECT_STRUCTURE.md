# LinkedIn Post Generator v3.0 - Project Structure

## 📁 Clean Folder Structure

```
D:\LinkedIn_post_generator\linkedin-post-generator-v3\
│
├── backend/                          # FastAPI Backend (v3.0)
│   ├── app/
│   │   ├── api/                     # API Routes (Controllers)
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── posts.py            # Post generation endpoints
│   │   │   ├── images.py           # Image generation endpoints
│   │   │   ├── users.py            # User management endpoints
│   │   │   └── analytics.py        # Analytics endpoints
│   │   │
│   │   ├── core/                    # Core Configuration
│   │   │   └── config.py           # App settings & env vars
│   │   │
│   │   ├── models/                  # Database Layer
│   │   │   ├── models.py           # SQLAlchemy ORM models
│   │   │   └── schemas.py          # Pydantic validation schemas
│   │   │
│   │   ├── services/                # Business Logic / AI Services
│   │   │   ├── llm_service.py              # LLM integration (Groq/OpenAI)
│   │   │   ├── user_profiling_service.py   # User style learning
│   │   │   ├── fact_checking_service.py    # Hallucination prevention
│   │   │   └── image_generation_service.py # Image generation
│   │   │
│   │   ├── workflows/               # AI Workflow Orchestration
│   │   │   └── post_generation_workflow.py # LangGraph workflow
│   │   │
│   │   ├── auth/                    # Authentication Logic
│   │   │   └── jwt.py              # JWT token handling
│   │   │
│   │   ├── db/                      # Database Configuration
│   │   │   └── database.py         # DB connection & session
│   │   │
│   │   └── main.py                 # FastAPI App Entry Point
│   │
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (DO NOT COMMIT)
│   ├── .env.example               # Environment template
│   ├── run.bat                     # Windows startup script
│   └── linkedin_generator.db       # SQLite database (auto-created)
│
├── frontend/                        # Next.js Frontend (v3.0)
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── layout.tsx         # Root layout
│   │   │   ├── page.tsx           # Landing page
│   │   │   ├── providers.tsx      # React Query provider
│   │   │   ├── globals.css        # Global styles (Tailwind)
│   │   │   │
│   │   │   ├── auth/              # Authentication Pages
│   │   │   │   ├── login/page.tsx     # Login page
│   │   │   │   └── register/page.tsx  # Registration page
│   │   │   │
│   │   │   └── dashboard/         # Dashboard Pages
│   │   │       ├── page.tsx            # Main dashboard
│   │   │       └── generate/page.tsx   # Post generator
│   │   │
│   │   ├── lib/                    # Utilities
│   │   │   └── api.ts             # Axios API client
│   │   │
│   │   └── stores/                 # State Management (Zustand)
│   │       ├── authStore.ts       # Authentication state
│   │       └── postStore.ts       # Post state
│   │
│   ├── package.json               # Node dependencies
│   ├── next.config.js             # Next.js configuration
│   ├── tsconfig.json              # TypeScript configuration
│   ├── tailwind.config.ts         # Tailwind configuration
│   └── .env.local                 # Frontend environment
│
├── legacy/                          # Old v2.0 code (reference only)
│   ├── agents/                    # Old agent system
│   ├── core/                      # Old core logic
│   ├── tools/                     # Old tools
│   ├── ui/                        # Old Streamlit UI
│   ├── prompts/                   # Old prompts
│   └── ...                        # Other old files
│
├── docs/                           # Documentation
│   └── (project docs here)
│
├── docker-compose.yml              # Docker setup
├── setup.sh                        # Linux/Mac setup script
├── README.md                       # This file
├── SETUP_GUIDE.md                  # Setup instructions
├── DEBUG_SUMMARY.md               # Debug report
└── BUILD_COMPLETE.md              # Build summary
```

## 🎯 Architecture Layers

### Backend (FastAPI) - Clean Architecture

```
┌─────────────────────────────────────────┐
│         API Layer (Routes)              │  ← app/api/*.py
│         HTTP Endpoints                  │
├─────────────────────────────────────────┤
│      Service Layer (Business Logic)     │  ← app/services/*.py
│      AI/ML Processing                   │
├─────────────────────────────────────────┤
│      Workflow Layer (Orchestration)     │  ← app/workflows/*.py
│      LangGraph State Machines           │
├─────────────────────────────────────────┤
│      Data Layer (Models & DB)           │  ← app/models/*.py
│      SQLAlchemy + Pydantic              │
└─────────────────────────────────────────┘
```

### Frontend (Next.js) - Feature-Based Structure

```
┌─────────────────────────────────────────┐
│         Pages (App Router)              │  ← src/app/
│         Routes & UI                     │
├─────────────────────────────────────────┤
│      Components (Reusable UI)           │  ← src/components/
│      Forms, Cards, Modals               │
├─────────────────────────────────────────┤
│      State Management (Zustand)         │  ← src/stores/
│      Client State                       │
├─────────────────────────────────────────┤
│      API Client (Axios)                 │  ← src/lib/api.ts
│      Server Communication               │
└─────────────────────────────────────────┘
```

## 🔧 Key Files Explained

### Backend Core Files

| File | Purpose | Layer |
|------|---------|-------|
| `app/main.py` | FastAPI app entry, CORS, routes | Entry Point |
| `app/core/config.py` | Environment variables, settings | Configuration |
| `app/api/posts.py` | Post generation endpoints | API/Controllers |
| `app/services/llm_service.py` | Groq/OpenAI integration | Business Logic |
| `app/workflows/post_generation_workflow.py` | LangGraph AI workflow | Orchestration |
| `app/models/models.py` | Database tables (SQLAlchemy) | Data Layer |
| `app/models/schemas.py` | Request/Response validation | Data Layer |
| `app/db/database.py` | DB connection setup | Infrastructure |

### Frontend Core Files

| File | Purpose | Layer |
|------|---------|-------|
| `src/app/page.tsx` | Landing page | Pages |
| `src/app/dashboard/page.tsx` | Main dashboard | Pages |
| `src/app/auth/login/page.tsx` | Login page | Pages |
| `src/lib/api.ts` | Axios client with interceptors | API Client |
| `src/stores/authStore.ts` | Auth state (Zustand) | State |
| `src/stores/postStore.ts` | Post state (Zustand) | State |

## 🚀 How It All Connects

### User Flow: Generate a Post

```
1. User visits http://localhost:3000
   ↓
2. Frontend: src/app/page.tsx (Landing page)
   ↓
3. User clicks "Get Started" → /auth/register
   ↓
4. Frontend: src/app/auth/register/page.tsx
   ↓
5. POST /api/auth/register → Backend: app/api/auth.py
   ↓
6. Backend creates user in SQLite DB
   ↓
7. User logs in → receives JWT token
   ↓
8. Frontend stores token in Zustand store
   ↓
9. Redirects to /dashboard
   ↓
10. User clicks "Generate Post" → /dashboard/generate
    ↓
11. Frontend: src/app/dashboard/generate/page.tsx
    ↓
12. POST /api/posts/generate → Backend: app/api/posts.py
    ↓
13. Backend starts LangGraph workflow:
    - Load user profile
    - Load writing style
    - Research topic
    - Generate variants
    - Fact-check
    - Score quality
    ↓
14. Returns generated post to frontend
    ↓
15. Frontend displays post with quality score
```

## 📝 Database (SQLite for Demo)

### Auto-Created Tables

- **users** - User accounts
- **brand_profiles** - Brand DNA
- **style_profiles** - Writing style patterns
- **posts** - Generated posts
- **images** - Generated images

### Database Location
`backend/linkedin_generator.db` (auto-created on first run)

## 🔐 Environment Configuration

### Backend (.env)
```bash
# Required
GROQ_API_KEY=your_key_here
DATABASE_URL=sqlite:///./linkedin_generator.db
SECRET_KEY=your-secret-key

# Optional
OPENAI_API_KEY=your_openai_key
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Where to Find What

### Looking for...

**Authentication Logic:**
- Backend: `app/api/auth.py` + `app/auth/jwt.py`
- Frontend: `src/app/auth/` + `src/stores/authStore.ts`

**Post Generation:**
- Backend: `app/api/posts.py` + `app/workflows/post_generation_workflow.py`
- Frontend: `src/app/dashboard/generate/page.tsx`

**AI Services:**
- LLM Integration: `app/services/llm_service.py`
- User Profiling: `app/services/user_profiling_service.py`
- Fact Checking: `app/services/fact_checking_service.py`
- Image Generation: `app/services/image_generation_service.py`

**Database Models:**
- `app/models/models.py` (SQLAlchemy)
- `app/models/schemas.py` (Pydantic)

**UI Components:**
- Pages: `src/app/`
- (Future components: `src/components/`)

## 🎓 For New Developers

### Quick Orientation

1. **Start Here:** `README.md` and `SETUP_GUIDE.md`
2. **Backend Entry:** `backend/app/main.py`
3. **Frontend Entry:** `frontend/src/app/page.tsx`
4. **API Docs:** http://localhost:8000/docs (when running)

### Understanding the Code

- **Backend follows:** API → Services → Workflows → Models pattern
- **Frontend follows:** Pages → Stores → API Client pattern
- **AI Logic:** All in `backend/app/services/` and `backend/app/workflows/`
- **Database:** SQLite for demo, easily switchable to PostgreSQL

## 🔄 Migration Path

### From v2.0 (Legacy) to v3.0

- Old code moved to `legacy/` folder for reference
- New architecture is cleaner and more scalable
- All v3.0 code is in `backend/` and `frontend/` folders

---

**Last Updated:** Current session
**Version:** 3.0.0
**Status:** Production Ready (Demo Mode with SQLite)
