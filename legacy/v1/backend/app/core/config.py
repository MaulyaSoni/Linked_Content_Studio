import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "LinkedIn Post Generator"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE_CHANGE_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "linkedin_generator"
    POSTGRES_PORT: int = 5432
    DATABASE_URI: str | None = None
    
    @property
    def sync_database_uri(self) -> str:
        if self.DATABASE_URI:
            return self.DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Providers
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    
    # Media Providers
    REPLICATE_API_TOKEN: str | None = None
    
    # Vector Database
    PINECONE_API_KEY: str | None = None
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_INDEX_NAME: str = "user-styles"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

settings = Settings()
