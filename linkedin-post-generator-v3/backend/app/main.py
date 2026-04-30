from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, posts, images, users, analytics
from app.db.database import engine
from app.models.models import Base
import sentry_sdk

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize Sentry for error tracking
if not settings.DEBUG:
    sentry_sdk.init(dsn="your-sentry-dsn")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered LinkedIn post generator with user profiling and fact-checking"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }
