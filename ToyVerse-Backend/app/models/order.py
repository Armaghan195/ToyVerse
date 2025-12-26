
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
import json
from datetime import datetime

from app.models.base import BaseModel

class Order(BaseModel):

    __tablename__ = "orders"

    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_details_json = Column(Text, nullable=False)
    items_json = Column(Text, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    payment_method = Column(String(50), nullable=False)

    user = relationship("User", back_populates="orders")

    @property
    def customer_details(self) -> dict:

        if self.customer_details_json:
            try:
                return json.loads(self.customer_details_json)
            except json.JSONDecodeError:
                return {}
        return {}

    @customer_details.setter
    def customer_details(self, value: dict) -> None:

        self.customer_details_json = json.dumps(value)

    @property
    def items(self) -> list:

        if self.items_json:
            try:
                return json.loads(self.items_json)
            except json.JSONDecodeError:
                return []
        return []

    @items.setter
    def items(self, value: list) -> None:

        self.items_json = json.dumps(value)

    def update_status(self, new_status: str) -> None:

        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        if new_status in valid_statuses:
            self.status = new_status

    def to_dict(self) -> dict:

        data = super().to_dict()
        data['customer_details'] = self.customer_details
        data['items'] = self.items
        return data

    def __repr__(self) -> str:

        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"
