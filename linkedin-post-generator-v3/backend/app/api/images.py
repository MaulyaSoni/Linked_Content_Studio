from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import schemas
from app.models.models import Image, Post
from app.services.image_generation_service import ImageGenerationService
from app.api.posts import get_current_user
from app.models.models import User

router = APIRouter()


@router.post("/generate", response_model=schemas.ImageResponse)
async def generate_image(
    request: schemas.ImageGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an image for a post."""
    
    # Get the post
    post = db.query(Post).filter(Post.id == request.post_id, Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Generate image
    image_service = ImageGenerationService()
    image_result = await image_service.generate_image_for_post(
        post_text=post.content,
        style=request.style,
    )
    
    # Save to database
    new_image = Image(
        post_id=request.post_id,
        image_url=image_result.url,
        prompt=image_result.prompt,
        style=image_result.style,
    )
    
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    
    return new_image


@router.get("/{image_id}", response_model=schemas.ImageResponse)
async def get_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific image."""
    
    image = db.query(Image).join(Post).filter(
        Image.id == image_id,
        Post.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return image
