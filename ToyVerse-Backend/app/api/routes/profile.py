
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Optional
import os
import shutil
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.api.dependencies import get_current_user, get_db
from app.core.security import verify_password, hash_password
from sqlalchemy.orm import Session

router = APIRouter(prefix="/profile", tags=["Profile"])

UPLOAD_DIR = "uploads/profile_pictures"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        profile_picture=current_user.profile_picture,
        created_at=current_user.created_at,
        permissions=current_user.get_permissions()
    )

@router.put("/update", response_model=UserResponse)
async def update_profile(
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    current_password: Optional[str] = Form(None),
    new_password: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:

    if full_name is not None:
        current_user.full_name = full_name

    if email is not None:

        existing_user = db.query(User).filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

        current_user.email = email

    if new_password:
        if not current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password required to set new password"
            )

        if not verify_password(current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        current_user.password_hash = hash_password(new_password)

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        profile_picture=current_user.profile_picture,
        created_at=current_user.created_at,
        permissions=current_user.get_permissions()
    )

@router.post("/upload-picture", response_model=dict)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:

    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{current_user.id}_{timestamp}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    if current_user.profile_picture:
        old_file_path = current_user.profile_picture.replace("/uploads/", "uploads/")
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except:
                pass

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    profile_picture_url = f"/uploads/profile_pictures/{filename}"
    current_user.profile_picture = profile_picture_url

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture": profile_picture_url
    }

@router.delete("/delete-picture", response_model=dict)
async def delete_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:

    if not current_user.profile_picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture to delete"
        )

    file_path = current_user.profile_picture.replace("/uploads/", "uploads/")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:

            pass

    current_user.profile_picture = None
    db.commit()

    return {"message": "Profile picture deleted successfully"}
