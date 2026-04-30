# Project Layout Guide

This project is organized to keep responsibilities clear and make onboarding faster.

## Top-level structure

- `backend/` - FastAPI API, authentication, persistence, and generation bridge service.
- `frontend/` - Next.js dashboard and user-facing workflows.
- `shared/` - cross-cutting types/utilities intended for both apps.
- `docs/` - architecture and implementation documentation.

## Backend structure (`backend/app`)

- `api/` - HTTP endpoints (`auth`, `posts`, `images`, `users`, `analytics`).
- `services/` - business logic and integration services.
- `workflows/` - orchestration logic.
- `models/` - SQLAlchemy + Pydantic models.
- `db/` - database session and engine setup.
- `core/` - configuration and application settings.

### Streamlit compatibility path

To preserve existing behavior from `app.py`, generation requests now flow through:

- `services/streamlit_compat_service.py` - adapts API requests into the proven `core.generator.LinkedInGenerator`.
- `api/posts.py` - persists results and returns Streamlit-compatible response fields.

## Frontend structure (`frontend/src`)

- `app/` - Next.js routes (`/dashboard`, `/auth`, `/dashboard/generate`).
- `features/post-generator/` - post generator feature constants and configuration.
- `stores/` - Zustand stores.
- `lib/` - API client and utility modules.

## Why this structure

- Keeps API concerns separate from generation internals.
- Preserves working Streamlit logic while serving Next.js clients.
- Makes folder intent obvious for new contributors.
