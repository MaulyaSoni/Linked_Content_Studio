from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import schemas
from app.models.models import Post, User
from app.auth.jwt import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.streamlit_compat_service import StreamlitCompatService

router = APIRouter()
security = HTTPBearer()
compat_service: StreamlitCompatService | None = None


def get_compat_service() -> StreamlitCompatService:
    """Lazily initialize heavy Streamlit-compatible generation service."""
    global compat_service
    if compat_service is None:
        compat_service = StreamlitCompatService()
    return compat_service


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


@router.post("/generate", response_model=schemas.CompatGenerateResponse)
async def generate_post(
    request: schemas.PostGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate content via Streamlit-compatible backend logic."""
    payload = request.model_dump()
    service = get_compat_service()

    post_type = (payload.get("post_type") or "simple_topic").lower()
    if post_type == "hackathon_project":
        result = service.generate_hackathon_post(payload)
        post_topic = payload.get("project_name") or payload.get("topic") or "Hackathon Post"
    else:
        result = service.generate_standard_post(payload)
        post_topic = payload.get("topic") or payload.get("github_url") or payload.get("text_input") or "Generated Post"

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error_message", "Generation failed"),
        )

    quality = result.get("quality_score")
    quality_value = None
    if isinstance(quality, (int, float)):
        quality_value = float(quality)
    elif isinstance(quality, dict) and quality:
        numeric_values = [v for v in quality.values() if isinstance(v, (int, float))]
        quality_value = float(sum(numeric_values) / len(numeric_values)) if numeric_values else None

    new_post = Post(
        user_id=current_user.id,
        topic=post_topic,
        content=result.get("post", ""),
        tone=payload.get("tone"),
        audience=payload.get("audience"),
        hashtags=result.get("hashtags_list") or [],
        quality_score=quality_value,
        fact_check_score=None,
    )

    db.add(new_post)
    db.commit()

    return result


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
