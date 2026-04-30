from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="LinkedIn Post Generator Backend API powering Advanced AI Operations",
        version="3.0.0"
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Note: Define your application router inclusion here as models and views grow
    # e.g., application.include_router(api_router, prefix=settings.API_V1_STR)

    return application

app = get_application()

@app.get("/health")
def read_health():
    return {"status": "ok", "message": "LinkedIn Post Generator Backend is running"}
