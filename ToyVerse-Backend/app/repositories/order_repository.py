from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.repositories.base_repository import BaseRepository
from app.models.order import Order

logger = logging.getLogger(__name__)

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_id(self, id: int) -> Optional[Order]:
        try:
            return self._db.query(Order).filter(Order.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting order by ID {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        try:
            return self._db.query(Order).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all orders: {e}")
            return []

    def create(self, entity: Order) -> Order:
        try:
            self._db.add(entity)
            if self._commit():
                self._refresh(entity)
                return entity
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error creating order: {e}")
            self._db.rollback()
            return None

    def update(self, id: int, data: Dict[str, Any]) -> Optional[Order]:
        try:
            order = self.get_by_id(id)
            if order:
                for key, value in data.items():
                    if hasattr(order, key) and key != 'id':
                        setattr(order, key, value)
                if self._commit():
                    self._refresh(order)
                    return order
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error updating order {id}: {e}")
            self._db.rollback()
            return None

    def delete(self, id: int) -> bool:
        try:
            order = self.get_by_id(id)
            if order:
                self._db.delete(order)
                return self._commit()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting order {id}: {e}")
            self._db.rollback()
            return False

    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        try:
            return (
                self._db.query(Order)
                .filter(Order.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting orders for user {user_id}: {e}")
            return []

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        try:
            return self._db.query(Order).filter(Order.order_number == order_number).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting order by number {order_number}: {e}")
            return None

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        try:
            return (
                self._db.query(Order)
                .filter(Order.status == status)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting orders by status {status}: {e}")
            return []
