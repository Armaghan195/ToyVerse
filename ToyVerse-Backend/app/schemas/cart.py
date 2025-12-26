from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class CartItemBase(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(default=1, ge=1, description="Quantity")

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1, description="New quantity")

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    created_at: datetime
    product: Optional[dict] = None
    subtotal: float

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total: Decimal
    item_count: int
