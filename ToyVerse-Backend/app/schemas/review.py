from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    text: Optional[str] = Field(None, description="Review text")

class ReviewCreate(ReviewBase):
    product_id: int = Field(..., description="Product ID")

class ReviewUpdate(ReviewBase):
    rating: Optional[int] = Field(None, ge=1, le=5)
    text: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: int
    product_id: int
    user_id: int
    created_at: datetime
    user: Optional[dict] = None

    class Config:
        from_attributes = True
