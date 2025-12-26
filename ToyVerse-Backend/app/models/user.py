
from typing import List
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class User(BaseModel):

    __tablename__ = "users"

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': 'role'
    }

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='customer')
    full_name = Column(String(100))
    profile_picture = Column(String(500))

    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    product_interactions = relationship("ProductInteraction", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")

    def get_permissions(self) -> List[str]:

        return ["read"]

    def can_perform(self, action: str) -> bool:

        return action in self.get_permissions()

    def __repr__(self) -> str:

        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

class Admin(User):

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

    def get_permissions(self) -> List[str]:

        return [
            "read",
            "write",
            "delete",
            "manage_products",
            "manage_users",
            "manage_orders",
            "view_analytics",
            "manage_reviews",
            "system_config",
            "view_logs"
        ]

    def is_admin(self) -> bool:

        return True

    def __repr__(self) -> str:

        return f"<Admin(id={self.id}, username={self.username})>"

class Customer(User):

    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }

    def get_permissions(self) -> List[str]:

        return [
            "read",
            "manage_cart",
            "place_orders",
            "write_reviews",
            "view_own_orders",
            "update_profile"
        ]

    def is_admin(self) -> bool:

        return False

    def can_review_product(self, product_id: int) -> bool:

        return "write_reviews" in self.get_permissions()

    def __repr__(self) -> str:

        return f"<Customer(id={self.id}, username={self.username})>"

def create_user(username: str, email: str, password_hash: str, role: str = 'customer') -> User:

    if role == 'admin':
        user = Admin(username=username, email=email, password_hash=password_hash, role='admin')
    else:
        user = Customer(username=username, email=email, password_hash=password_hash, role='customer')

    return user
