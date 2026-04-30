# LinkedIn Post Generator Workspace Structure

This workspace now separates legacy versions from the active Next.js + FastAPI implementation.

## Root layout

- `linkedin-post-generator-v3/` - active product (current Next.js frontend + FastAPI backend).
- `legacy/v1/` - older web-app style implementation artifacts.
- `legacy/v2/app/` - Streamlit-based implementation and supporting modules.
- `legacy/shared/` - archived cross-version documents and reports.
- `.venv/`, `.qoder/` - local tooling/environment folders.
- `.env`, `.gitignore` - workspace-level config.

## Legacy organization details

### `legacy/v1/`
- `backend/`
- `frontend/`
- `package.json`
- `package-lock.json`
- `node_modules/`

### `legacy/v2/app/`
- `app.py`
- `core/`, `ui/`, `prompts/`, `chains/`
- `loaders/`, `tools/`, `utils/`, `data/`, `tests/`, `agents/`
- `requirements.txt`
- `README.md`
- `SYSTEM_DOCUMENTATION.md`
- `.env.example`, `.env.template`
- other v2 support files

### `legacy/shared/`
- `ADVANCED_FEATURES_IMPLEMENTATION.md`
- `TECH_STACK_REVISION_v3.0.md`
- `COMPLETE_v3.0_IMPLEMENTATION_ROADMAP.txt`
- `COMPLETE_v3.0_IMPLEMENTATION_ROADMAP (1).txt`
- `logs/`

## Clean-up applied

- Removed Python cache directory from legacy v2 app.
- Archived non-runtime legacy logs into `legacy/shared/logs/`.

## Active development location

Use only:

- `linkedin-post-generator-v3/frontend/`
- `linkedin-post-generator-v3/backend/`

for ongoing product development and debugging.
