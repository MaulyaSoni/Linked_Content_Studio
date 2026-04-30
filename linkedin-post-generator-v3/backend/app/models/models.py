from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    """User model for authentication and profile."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="user")
    brand_profile = relationship("BrandProfile", back_populates="user", uselist=False)
    style_profile = relationship("StyleProfile", back_populates="user", uselist=False)


class BrandProfile(Base):
    """Brand DNA and voice profile for user."""
    
    __tablename__ = "brand_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    target_audience = Column(String, nullable=True)
    brand_voice = Column(String, nullable=True)  # professional, casual, humorous, etc.
    core_values = Column(JSON, nullable=True)  # List of values
    content_pillars = Column(JSON, nullable=True)  # Topics they write about
    competitor_urls = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="brand_profile")


class StyleProfile(Base):
    """User's unique writing style profile."""
    
    __tablename__ = "style_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    tone = Column(String, default="professional")
    vocabulary_level = Column(String, default="intermediate")
    personality_archetype = Column(String, default="thought_leader")
    emoji_usage = Column(Boolean, default=True)
    storytelling_style = Column(String, default="narrative")
    cta_preference = Column(String, default="question")
    audience_connection = Column(String, default="direct")
    structure_patterns = Column(JSON, nullable=True)  # avg_length, questions_per_post, etc.
    core_themes = Column(JSON, nullable=True)  # List of themes
    liked_elements = Column(JSON, nullable=True)
    improvement_notes = Column(JSON, nullable=True)
    performance_history = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="style_profile")


class Post(Base):
    """Generated LinkedIn posts."""
    
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tone = Column(String, nullable=True)
    audience = Column(String, nullable=True)
    hashtags = Column(JSON, nullable=True)
    quality_score = Column(Float, nullable=True)
    fact_check_score = Column(Float, nullable=True)
    status = Column(String, default="draft")  # draft, published, scheduled
    published_at = Column(DateTime, nullable=True)
    linkedin_post_id = Column(String, nullable=True)
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="posts")
    images = relationship("Image", back_populates="post")


class Image(Base):
    """Generated images for posts."""
    
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    image_url = Column(String, nullable=False)
    prompt = Column(Text, nullable=True)
    style = Column(String, default="modern")
    width = Column(Integer, default=1200)
    height = Column(Integer, default=628)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    post = relationship("Post", back_populates="images")
