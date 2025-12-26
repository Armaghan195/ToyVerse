
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):

    title: str = Field(..., min_length=1, max_length=200, description="Product title")
    price: Decimal = Field(..., gt=0, description="Product price (must be positive)")
    category: str = Field(..., min_length=1, max_length=50, description="Product category")
    stock: int = Field(default=0, ge=0, description="Stock quantity")
    rating: int = Field(default=0, ge=0, le=5, description="Product rating (0-5)")
    icon: Optional[str] = Field(None, max_length=10, description="Product icon/emoji")
    description: Optional[str] = Field(None, description="Short product description")
    detailed_description: Optional[str] = Field(None, description="Detailed product description")
    images: List[str] = Field(default_factory=list, description="Product image URLs")

class ProductCreate(ProductBase):

    pass

class ProductUpdate(BaseModel):

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    stock: Optional[int] = Field(None, ge=0)
    rating: Optional[int] = Field(None, ge=0, le=5)
    icon: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    images: Optional[List[str]] = None

class ProductResponse(ProductBase):

    id: int
    created_at: datetime
    updated_at: datetime
    is_in_stock: bool = Field(..., description="Whether product is in stock")
    formatted_price: str = Field(..., description="Formatted price string")

    class Config:

        from_attributes = True

class ProductFilter(BaseModel):

    category: Optional[str] = None
    price_max: Optional[Decimal] = None
    rating: Optional[int] = Field(None, ge=0, le=5)
    search: Optional[str] = None
    in_stock: Optional[bool] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=100)
