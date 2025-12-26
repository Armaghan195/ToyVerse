
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Numeric, Text
from sqlalchemy.orm import relationship
import json

from app.models.base import BaseModel

class Product(BaseModel):

    __tablename__ = "products"

    title = Column(String(200), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    stock = Column(Integer, default=0, nullable=False)
    rating = Column(Integer, default=0)
    icon = Column(String(10))
    images_json = Column(Text)
    description = Column(Text)
    detailed_description = Column(Text)

    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    interactions = relationship("ProductInteraction", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("Wishlist", back_populates="product", cascade="all, delete-orphan")

    @property
    def images(self) -> List[str]:

        if self.images_json:
            try:
                return json.loads(self.images_json)
            except json.JSONDecodeError:
                return []
        return []

    @images.setter
    def images(self, value: List[str]) -> None:

        self.images_json = json.dumps(value)

    @property
    def is_in_stock(self) -> bool:

        return self.stock > 0

    @property
    def formatted_price(self) -> str:

        return f"${float(self.price):.2f}"

    def decrease_stock(self, quantity: int) -> bool:

        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False

    def increase_stock(self, quantity: int) -> None:

        self.stock += quantity

    def update_rating(self, new_rating: int) -> None:

        if 1 <= new_rating <= 5:
            self.rating = new_rating

    def to_dict(self) -> dict:

        data = super().to_dict()
        data['images'] = self.images
        data['is_in_stock'] = self.is_in_stock
        data['formatted_price'] = self.formatted_price
        return data

    def __repr__(self) -> str:

        return f"<Product(id={self.id}, title={self.title}, price={self.price})>"
