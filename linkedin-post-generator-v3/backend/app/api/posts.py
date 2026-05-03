from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.models import schemas
from app.models.models import Post, User
from app.auth.jwt import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.generation_service import GenerationService
from app.services.linkedin_service import LinkedInService

router = APIRouter()
security = HTTPBearer()

# Initialize core services
generation_service = GenerationService()
linkedin_service = LinkedInService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@router.post("/publish", response_model=schemas.LinkedInPublishResponse)
async def publish_post(
    request: schemas.LinkedInPublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a post to LinkedIn."""
    
    # 1. Fetch the post from DB
    post = db.query(Post).filter(Post.id == request.post_id, Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    from app.core.config import settings
    
    access_token = request.access_token or settings.LINKEDIN_ACCESS_TOKEN
    user_id = request.user_id or settings.LINKEDIN_USER_ID
    
    if not access_token or not user_id:
        return {
            "success": False,
            "error": "LinkedIn credentials missing. Please configure them in .env or connect your account."
        }
    
    # 2. Publish to LinkedIn
    result = await linkedin_service.publish_post(
        content=post.content,
        access_token=access_token,
        user_id=user_id
    )
    
    if result["success"]:
        # 3. Update post status in DB
        post.status = "published"
        post.published_at = datetime.utcnow()
        post.linkedin_post_id = result["post_urn"]
        db.commit()
        
        return {
            "success": True,
            "post_urn": result["post_urn"]
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "Unknown error occurred during publishing")
        }





@router.post("/generate")
async def generate_post(
    request: schemas.PostGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate personalized LinkedIn post based on user profile.
    """
    
    try:
        # Generate post
        result = await generation_service.generate_post(
            topic=request.topic,
            user_id=current_user.id,
            db=db,
            tone=request.tone if hasattr(request, 'tone') else None,
            content_type=request.content_type if hasattr(request, 'content_type') else "simple_topic",
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Generation failed")
            )
        
        hashtags_list = result["hashtags"]
        hashtags_str = " ".join(hashtags_list) if hashtags_list else ""
        
        # Save to database
        db_post = Post(
            user_id=current_user.id,
            content=result["post"],
            hashtags=hashtags_list,
            quality_score=result["quality_score"],
            topic=request.topic,
            created_at=datetime.utcnow()
        )
        
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return schemas.CompatGenerateResponse(
            post=result["post"],
            hashtags=hashtags_str,
            hashtags_list=hashtags_list,
            quality_score=result["quality_score"],
            tokens_used=result["tokens_used"],
            mode_used="personalized_advanced",
            success=True,
            post_id=db_post.id,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/history", response_model=schemas.PostListResponse)
async def get_post_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's post history."""
    
    posts = db.query(Post).filter(Post.user_id == current_user.id).order_by(Post.created_at.desc()).all()
    
    return {
        "posts": posts,
        "total": len(posts)
    }


@router.get("/{post_id}", response_model=schemas.PostResponse)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific post."""
    
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post."""
    
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}
