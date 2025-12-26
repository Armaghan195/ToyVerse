
from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.orm import Session, joinedload
from app.models.wishlist import Wishlist
from app.repositories.base_repository import BaseRepository

class WishlistRepository(BaseRepository[Wishlist]):

    def __init__(self, db: Session):
        super().__init__(Wishlist, db)

    def get_by_id(self, id: int) -> Optional[Wishlist]:

        try:
            return self._db.query(Wishlist).filter(Wishlist.id == id).first()
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting wishlist item by id {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Wishlist]:

        try:
            return (
                self._db.query(Wishlist)
                .order_by(Wishlist.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting all wishlist items: {e}")
            return []

    def create(self, entity: Wishlist) -> Optional[Wishlist]:

        try:
            self._db.add(entity)
            if self._commit():
                self._refresh(entity)
                return entity
            return None
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating wishlist item: {e}")
            self._db.rollback()
            return None

    def update(self, id: int, data: Dict[str, Any]) -> Optional[Wishlist]:

        try:
            item = self.get_by_id(id)
            if item:
                for key, value in data.items():
                    if hasattr(item, key) and key != 'id':
                        setattr(item, key, value)
                if self._commit():
                    self._refresh(item)
                    return item
            return None
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating wishlist item {id}: {e}")
            self._db.rollback()
            return None

    def delete(self, id: int) -> bool:

        try:
            item = self.get_by_id(id)
            if item:
                self._db.delete(item)
                return self._commit()
            return False
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting wishlist item {id}: {e}")
            self._db.rollback()
            return False

    def get_user_wishlist(self, user_id: int) -> List[Wishlist]:

        return self._db.query(Wishlist).options(
            joinedload(Wishlist.product)
        ).filter(
            Wishlist.user_id == user_id
        ).all()

    def find_by_user_and_product(self, user_id: int, product_id: int) -> Optional[Wishlist]:

        return self._db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id
        ).first()

    def delete_by_user_and_product(self, user_id: int, product_id: int) -> bool:

        item = self.find_by_user_and_product(user_id, product_id)
        if item:
            self._db.delete(item)
            self._db.commit()
            return True
        return False

    def is_in_wishlist(self, user_id: int, product_id: int) -> bool:

        return self.find_by_user_and_product(user_id, product_id) is not None

    def get_wishlist_product_ids(self, user_id: int) -> List[int]:

        items = self._db.query(Wishlist.product_id).filter(
            Wishlist.user_id == user_id
        ).all()
        return [item[0] for item in items]
