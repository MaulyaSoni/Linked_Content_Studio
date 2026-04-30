# Backend Feature Reference (v3)

This document explains how the FastAPI backend works, where each feature lives, and the request flow.

## Backend entry points

- `backend/app/main.py`
  - Creates FastAPI app instance.
  - Registers CORS middleware.
  - Includes all API routers.
  - Exposes root endpoint and `/api/health`.

- `backend/app/core/config.py`
  - Central settings loader from env (`BaseSettings`).
  - Holds app metadata, DB URL, JWT config, CORS origins, optional provider keys.

- `backend/app/db/database.py`
  - SQLAlchemy engine/session creation.
  - SQLite compatibility handling.
  - `get_db()` dependency for API routes.

## API surface and file mapping

### 1) Authentication

- **Files**
  - `backend/app/api/auth.py`
  - `backend/app/auth/jwt.py`
  - `backend/app/models/models.py` (`User`)
  - `backend/app/models/schemas.py` (`UserCreate`, `UserLogin`, `Token`, `UserResponse`)

- **Endpoints**
  - `POST /api/auth/register`
  - `POST /api/auth/login`

- **Behavior**
  - Register validates uniqueness by email and stores hashed password.
  - Login verifies password and returns JWT access token.

### 2) Post generation

- **Files**
  - `backend/app/api/posts.py`
  - `backend/app/services/streamlit_compat_service.py`
  - `backend/app/models/models.py` (`Post`)
  - `backend/app/models/schemas.py` (`PostGenerateRequest`, `CompatGenerateResponse`, history models)
  - Legacy generation source used by compat layer:
    - `legacy/v2/app/core/generator.py`
    - `legacy/v2/app/core/models.py`

- **Endpoints**
  - `POST /api/posts/generate`
  - `GET /api/posts/history`
  - `GET /api/posts/{post_id}`
  - `DELETE /api/posts/{post_id}`

- **Behavior**
  - Authenticated endpoint validates bearer token.
  - Uses compatibility service to map API payload into legacy working generation classes.
  - Persists generated result into `posts` table.
  - Supports post types:
    - `simple_topic`
    - `advanced_github`
    - `hackathon_project`

### 3) Images

- **Files**
  - `backend/app/api/images.py`
  - `backend/app/services/image_generation_service.py`
  - `backend/app/models/models.py` (`Image`)
  - `backend/app/models/schemas.py` (`ImageGenerateRequest`, `ImageResponse`)

- **Endpoints**
  - Mounted under `/api/images/*` in `main.py`.

- **Behavior**
  - Generates and stores image metadata associated with a post.

### 4) Users / profiles

- **Files**
  - `backend/app/api/users.py`
  - `backend/app/models/models.py` (`BrandProfile`, `StyleProfile`)
  - `backend/app/models/schemas.py` (profile response schemas)
  - `backend/app/services/user_profiling_service.py`

- **Behavior**
  - User profile and style-related data retrieval/update paths.

### 5) Analytics

- **Files**
  - `backend/app/api/analytics.py`
  - `backend/app/models/models.py` (`Post`, usage metrics fields)
  - `backend/app/models/schemas.py` (`AnalyticsOverview`)

- **Behavior**
  - Aggregates post records into overview metrics.

## Service layer details

- `backend/app/services/llm_service.py`
  - LLM calls (Groq/OpenAI).
  - OpenAI import is optional and fails gracefully if unavailable.

- `backend/app/services/fact_checking_service.py`
  - Fact-check pipeline and confidence scoring.

- `backend/app/services/user_profiling_service.py`
  - User style/profile modeling.

- `backend/app/services/image_generation_service.py`
  - Prompt/image generation orchestration.

- `backend/app/services/streamlit_compat_service.py`
  - Bridge from FastAPI request models to legacy v2 generator (stable behavior parity).

## Models and persistence

- `backend/app/models/models.py`
  - SQLAlchemy entities:
    - `User`
    - `BrandProfile`
    - `StyleProfile`
    - `Post`
    - `Image`

- `backend/app/models/schemas.py`
  - Pydantic request/response models for every API category.

## Runtime flow (generate post)

1. Frontend calls `POST /api/posts/generate`.
2. `api/posts.py` authenticates token and parses request schema.
3. `streamlit_compat_service.py` adapts payload to v2 generation model.
4. Legacy generator produces post output.
5. API stores the generated post in DB and returns structured response.

## Environment dependencies

- Required runtime libs:
  - `fastapi`, `uvicorn`, `sqlalchemy`, `python-jose[cryptography]`, `passlib`, `bcrypt`.
- AI/runtime libs:
  - `langchain`, `langchain-groq`, optional `langchain-openai`, `openai`.
- Monitoring:
  - `sentry-sdk[fastapi]`.

## Important operational note

Always run backend from:

- `linkedin-post-generator-v3/backend`

with:

```bash
python -m uvicorn app.main:app --port 8000
```
