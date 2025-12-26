
from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class CartItem(BaseModel):

    __tablename__ = "cart_items"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

    @property
    def subtotal(self) -> float:

        if self.product:
            return float(self.product.price) * self.quantity
        return 0.0

    def update_quantity(self, quantity: int) -> bool:

        if quantity > 0 and self.product and quantity <= self.product.stock:
            self.quantity = quantity
            return True
        return False

    def to_dict(self) -> dict:

        data = super().to_dict()
        data['subtotal'] = self.subtotal
        if self.product:
            data['product'] = {
                'id': self.product.id,
                'title': self.product.title,
                'price': float(self.product.price),
                'icon': self.product.icon,
                'stock': self.product.stock
            }
        return data

    def __repr__(self) -> str:

        return f"<CartItem(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})>"
