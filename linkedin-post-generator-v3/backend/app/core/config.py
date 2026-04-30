from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "LinkedIn Post Generator v3.0"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = False
    
    # API Keys
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
    PINECONE_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./linkedin_generator.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/api/auth/linkedin/callback"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
