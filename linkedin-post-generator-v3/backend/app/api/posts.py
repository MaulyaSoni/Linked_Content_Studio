from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import json
from app.db.database import get_db
from app.models import schemas
from app.models.models import Post, User
from app.auth.jwt import decode_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.linkedin_service import LinkedInService
from app.workflows.post_generation_workflow import run_post_generation_workflow

router = APIRouter()
security = HTTPBearer()

# Initialize core services
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





@router.post("/generate", response_model=schemas.CompatGenerateResponse)
async def generate_post(
    request: schemas.PostGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a LinkedIn post using the workflow."""
    result = await run_post_generation_workflow(
        user_id            = str(current_user.id),
        topic              = request.topic,
        db                 = db,
        content_type       = request.content_type,
        tone_override      = request.tone,
        additional_context = request.additional_context,
    )
    
    if result["success"]:
        # Save to database
        db_post = Post(
            user_id=current_user.id,
            content=result["post"],
            hashtags=result["hashtags"],
            quality_score=result["quality_score"],
            content_type=request.content_type,
            topic=request.topic,
            created_at=datetime.utcnow(),
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return {
            "success": True,
            "post": result["post"],
            "hashtags": result["hashtags"],
            "quality_score": result["quality_score"],
            "post_id": str(db_post.id),
            "mode_used": result["mode_used"],
            "tokens_used": result.get("tokens_used", 0),
            "node_trace": result.get("node_trace"),
            "has_history": result.get("has_history")
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Generation failed")
        )


@router.post("/generate/stream")
async def generate_post_stream(
    request: schemas.PostGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Streaming version — sends Server-Sent Events with node progress.
    """

    async def event_generator():
        # Step signals
        steps = [
            ("analyzing",  "Analyzing your writing style..."),
            ("researching","Researching the topic..."),
            ("drafting",   "Writing first draft..."),
            ("critiquing", "Reviewing for authenticity..."),
            ("polishing",  "Polishing final post..."),
        ]

        for step_id, message in steps:
            yield f"data: {json.dumps({'type': 'progress', 'step': step_id, 'message': message})}\n\n"
            await asyncio.sleep(0.1)

        # Run actual workflow
        result = await run_post_generation_workflow(
            user_id            = str(current_user.id),
            topic              = request.topic,
            db                 = db,
            content_type       = getattr(request, "content_type", "simple_topic"),
            tone_override      = getattr(request, "tone", None),
            additional_context = getattr(request, "additional_context", ""),
        )

        if result["success"]:
            # Save to DB
            db_post = Post(
                user_id       = current_user.id,
                content       = result["post"],
                hashtags      = result["hashtags"],
                quality_score = result["quality_score"],
                content_type  = getattr(request, "content_type", "simple_topic"),
                topic         = request.topic,
                created_at    = datetime.utcnow(),
            )
            db.add(db_post)
            db.commit()
            db.refresh(db_post)

            # Send final result
            yield f"data: {json.dumps({'type': 'result', 'data': {'post': result['post'], 'hashtags': result['hashtags'], 'quality_score': result['quality_score'], 'post_id': str(db_post.id), 'mode_used': result['mode_used'], 'node_trace': result.get('node_trace'), 'has_history': result.get('has_history')}})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'error', 'message': result.get('error', 'Generation failed')})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
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


@router.put("/{post_id}", response_model=schemas.PostResponse)
async def update_post(
    post_id: int,
    request: schemas.PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific post."""
    
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if request.content is not None:
        post.content = request.content
    if request.hashtags is not None:
        # Store as space-separated string if that's how it's stored in DB
        post.hashtags = " ".join(request.hashtags)
    if request.topic is not None:
        post.topic = request.topic
    
    db.commit()
    db.refresh(post)
    
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
