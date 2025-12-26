from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.repositories.base_repository import BaseRepository
from app.models.cart import CartItem

logger = logging.getLogger(__name__)

class CartRepository(BaseRepository[CartItem]):
    def __init__(self, db: Session):
        super().__init__(CartItem, db)

    def get_by_id(self, id: int) -> Optional[CartItem]:
        try:
            return self._db.query(CartItem).filter(CartItem.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cart item by ID {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[CartItem]:
        try:
            return self._db.query(CartItem).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all cart items: {e}")
            return []

    def create(self, entity: CartItem) -> CartItem:
        try:
            self._db.add(entity)
            if self._commit():
                self._refresh(entity)
                return entity
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error creating cart item: {e}")
            self._db.rollback()
            return None

    def update(self, id: int, data: Dict[str, Any]) -> Optional[CartItem]:
        try:
            cart_item = self.get_by_id(id)
            if cart_item:
                for key, value in data.items():
                    if hasattr(cart_item, key) and key != 'id':
                        setattr(cart_item, key, value)
                if self._commit():
                    self._refresh(cart_item)
                    return cart_item
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error updating cart item {id}: {e}")
            self._db.rollback()
            return None

    def delete(self, id: int) -> bool:
        try:
            cart_item = self.get_by_id(id)
            if cart_item:
                self._db.delete(cart_item)
                return self._commit()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting cart item {id}: {e}")
            self._db.rollback()
            return False

    def get_by_user_id(self, user_id: int) -> List[CartItem]:
        try:
            return self._db.query(CartItem).filter(CartItem.user_id == user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cart items for user {user_id}: {e}")
            return []

    def get_by_user_and_product(self, user_id: int, product_id: int) -> Optional[CartItem]:
        try:
            return self._db.query(CartItem).filter(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting cart item: {e}")
            return None

    def clear_user_cart(self, user_id: int) -> bool:
        try:
            self._db.query(CartItem).filter(CartItem.user_id == user_id).delete()
            return self._commit()
        except SQLAlchemyError as e:
            logger.error(f"Error clearing cart for user {user_id}: {e}")
            self._db.rollback()
            return False
