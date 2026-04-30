from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import schemas
from app.models.models import User, BrandProfile, StyleProfile
from app.api.posts import get_current_user

router = APIRouter()


@router.get("/profile", response_model=schemas.UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile."""
    return current_user


@router.put("/profile", response_model=schemas.UserResponse)
async def update_profile(
    profile_data: schemas.UserBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    
    current_user.full_name = profile_data.full_name
    current_user.linkedin_url = profile_data.linkedin_url
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/style", response_model=schemas.StyleProfileResponse)
async def get_style_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's style profile."""
    
    style = db.query(StyleProfile).filter(StyleProfile.user_id == current_user.id).first()
    
    if not style:
        # Create default style profile
        style = StyleProfile(user_id=current_user.id)
        db.add(style)
        db.commit()
        db.refresh(style)
    
    return style


@router.get("/brand", response_model=schemas.BrandProfileResponse)
async def get_brand_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's brand profile."""
    
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    return brand


@router.put("/brand", response_model=schemas.BrandProfileResponse)
async def update_brand_profile(
    brand_data: schemas.BrandProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update or create brand profile."""
    
    brand = db.query(BrandProfile).filter(BrandProfile.user_id == current_user.id).first()
    
    if brand:
        # Update existing
        for key, value in brand_data.dict().items():
            setattr(brand, key, value)
    else:
        # Create new
        brand = BrandProfile(user_id=current_user.id, **brand_data.dict())
        db.add(brand)
    
    db.commit()
    db.refresh(brand)
    
    return brand
