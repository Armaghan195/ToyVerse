
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.product import ProductResponse

class WishlistBase(BaseModel):

    product_id: int = Field(..., description="Product ID")

class WishlistCreate(WishlistBase):

    pass

class WishlistResponse(BaseModel):

    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

class WishlistProductIds(BaseModel):

    product_ids: list[int]
