from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: int
    title: str
    price: Decimal
    quantity: int
    subtotal: Decimal

class CustomerDetailsBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    postal_code: str = Field(..., min_length=1)

class OrderCreate(BaseModel):
    customer_details: CustomerDetailsBase
    payment_method: str = Field(default="COD", description="Payment method")

class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Order status")

class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    customer_details: Dict[str, Any]
    items: List[Dict[str, Any]]
    total: Decimal
    status: str
    payment_method: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
