from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models import schemas
from app.models.models import Post
from app.api.posts import get_current_user
from app.models.models import User

router = APIRouter()


@router.get("/overview", response_model=schemas.AnalyticsOverview)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics overview."""
    
    # Get post statistics
    total_posts = db.query(func.count(Post.id)).filter(Post.user_id == current_user.id).scalar()
    published_posts = db.query(func.count(Post.id)).filter(
        Post.user_id == current_user.id,
        Post.status == "published"
    ).scalar()
    
    # Get average scores
    avg_quality = db.query(func.avg(Post.quality_score)).filter(
        Post.user_id == current_user.id,
        Post.quality_score.isnot(None)
    ).scalar() or 0.0
    
    avg_engagement = db.query(func.avg(Post.engagement_rate)).filter(
        Post.user_id == current_user.id
    ).scalar() or 0.0
    
    total_impressions = db.query(func.sum(Post.impressions)).filter(
        Post.user_id == current_user.id
    ).scalar() or 0
    
    return {
        "total_posts": total_posts,
        "published_posts": published_posts,
        "avg_quality_score": round(float(avg_quality), 2),
        "avg_engagement_rate": round(float(avg_engagement), 2),
        "total_impressions": total_impressions,
    }


@router.get("/posts")
async def get_post_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed post analytics."""
    
    posts = db.query(Post).filter(
        Post.user_id == current_user.id
    ).order_by(Post.created_at.desc()).limit(10).all()
    
    return {
        "posts": [
            {
                "id": post.id,
                "topic": post.topic,
                "quality_score": post.quality_score,
                "engagement_rate": post.engagement_rate,
                "impressions": post.impressions,
                "created_at": post.created_at,
            }
            for post in posts
        ]
    }
