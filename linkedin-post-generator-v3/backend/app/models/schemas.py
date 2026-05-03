from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    linkedin_url: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Brand Profile Schemas
class BrandProfileCreate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    brand_voice: Optional[str] = None
    core_values: Optional[List[str]] = None
    content_pillars: Optional[List[str]] = None
    competitor_urls: Optional[List[str]] = None


class BrandProfileResponse(BrandProfileCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Style Profile Schemas
class StyleProfileResponse(BaseModel):
    id: int
    user_id: int
    tone: str
    vocabulary_level: str
    personality_archetype: str
    emoji_usage: bool
    storytelling_style: str
    cta_preference: str
    audience_connection: str
    structure_patterns: Optional[dict] = None
    core_themes: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Post Schemas
class PostGenerateRequest(BaseModel):
    post_type: Optional[str] = "simple_topic"  # simple_topic | advanced_github | hackathon_project
    mode: Optional[str] = "simple"
    topic: Optional[str] = ""
    tone: Optional[str] = "professional"
    audience: Optional[str] = None
    context: Optional[str] = None
    content_type: Optional[str] = "general"
    github_url: Optional[str] = None
    text_input: Optional[str] = None
    user_key_message: Optional[str] = None
    tags_people: Optional[List[str]] = None
    tags_organizations: Optional[List[str]] = None
    include_hashtags: Optional[bool] = True
    include_caption: Optional[bool] = False
    max_length: Optional[int] = 2000
    
    @validator('topic')
    def topic_not_empty(cls, v):
        if v is None:
            return ""
        return v.strip()


class PostResponse(BaseModel):
    id: int
    user_id: int
    topic: str
    content: str
    tone: Optional[str]
    hashtags: Optional[List[str]]
    quality_score: Optional[float]
    fact_check_score: Optional[float]
    status: str
    created_at: datetime
    
    @validator('hashtags', pre=True)
    def parse_hashtags(cls, v):
        if isinstance(v, str):
            return v.split() if v else []
        return v
    
    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int


class CompatGenerateResponse(BaseModel):
    success: bool
    post: str
    hashtags: Optional[str] = None
    hashtags_list: Optional[List[str]] = None
    caption: Optional[str] = None
    mode_used: str
    quality_score: Optional[dict | float | int] = None
    hook_options: Optional[dict] = None
    generation_time: float = 0.0
    tokens_used: int = 0
    achievement_level: Optional[str] = None
    estimated_reach: Optional[str] = None
    error_message: Optional[str] = None


# Image Schemas
class ImageGenerateRequest(BaseModel):
    post_id: int
    style: Optional[str] = "modern"
    custom_prompt: Optional[str] = None


class ImageResponse(BaseModel):
    id: int
    post_id: int
    image_url: str
    prompt: Optional[str]
    style: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsOverview(BaseModel):
    total_posts: int
    published_posts: int
    avg_quality_score: float
    avg_engagement_rate: float
    total_impressions: int


# Fact Check Schemas
class FactCheckResult(BaseModel):
    confidence_score: float
    is_safe: bool
    total_claims: int
    verified_claims: int
    flagged_claims: List[dict]
# LinkedIn Schemas
class LinkedInPublishRequest(BaseModel):
    post_id: int
    access_token: Optional[str] = None
    user_id: Optional[str] = None

class LinkedInPublishResponse(BaseModel):
    success: bool
    post_urn: Optional[str] = None
    error: Optional[str] = None
