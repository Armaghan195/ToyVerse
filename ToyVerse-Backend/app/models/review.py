
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Review(BaseModel):

    __tablename__ = "reviews"

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(Text)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def is_valid_rating(self) -> bool:

        return 1 <= self.rating <= 5

    def to_dict(self) -> dict:

        data = super().to_dict()
        if self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username
            }
        return data

    def __repr__(self) -> str:

        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating})>"
