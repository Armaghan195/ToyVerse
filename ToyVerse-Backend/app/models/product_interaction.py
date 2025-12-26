
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import BaseModel

class ProductInteraction(BaseModel):

    __tablename__ = 'product_interactions'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)

    interaction_type = Column(String(50), nullable=False)
    session_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)

    user = relationship("User", back_populates="product_interactions")
    product = relationship("Product", back_populates="interactions")

    def __repr__(self):
        return f"<ProductInteraction(user_id={self.user_id}, product_id={self.product_id}, type={self.interaction_type})>"

    def to_dict(self):

        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'interaction_type': self.interaction_type,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
