from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
import os
import uuid
from pathlib import Path

from app.models.user import Admin
from app.api.dependencies import get_current_admin

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("uploads/products")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024

def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

def save_file(file: UploadFile) -> str:
    ensure_upload_dir()

    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        buffer.write(content)

    return f"/uploads/products/{unique_filename}"

@router.post("/product-image", status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin)
):
    validate_file(file)

    try:
        file_url = save_file(file)
        return {
            "filename": file.filename,
            "url": file_url,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.post("/product-images", status_code=status.HTTP_201_CREATED)
async def upload_multiple_product_images(
    files: List[UploadFile] = File(...),
    current_admin: Admin = Depends(get_current_admin)
):
    if len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 files allowed"
        )

    uploaded_files = []
    errors = []

    for file in files:
        try:
            validate_file(file)
            file_url = save_file(file)
            uploaded_files.append({
                "filename": file.filename,
                "url": file_url
            })
        except HTTPException as e:
            errors.append({
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })

    return {
        "uploaded": uploaded_files,
        "errors": errors,
        "message": f"Uploaded {len(uploaded_files)} of {len(files)} files"
    }
