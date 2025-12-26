from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.repositories.base_repository import BaseRepository
from app.models.review import Review

logger = logging.getLogger(__name__)

class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def get_by_id(self, id: int) -> Optional[Review]:
        try:
            return self._db.query(Review).filter(Review.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting review by ID {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Review]:
        try:
            return self._db.query(Review).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all reviews: {e}")
            return []

    def create(self, entity: Review) -> Review:
        try:
            self._db.add(entity)
            if self._commit():
                self._refresh(entity)
                return entity
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error creating review: {e}")
            self._db.rollback()
            return None

    def update(self, id: int, data: Dict[str, Any]) -> Optional[Review]:
        try:
            review = self.get_by_id(id)
            if review:
                for key, value in data.items():
                    if hasattr(review, key) and key != 'id':
                        setattr(review, key, value)
                if self._commit():
                    self._refresh(review)
                    return review
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error updating review {id}: {e}")
            self._db.rollback()
            return None

    def delete(self, id: int) -> bool:
        try:
            review = self.get_by_id(id)
            if review:
                self._db.delete(review)
                return self._commit()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting review {id}: {e}")
            self._db.rollback()
            return False

    def get_by_product_id(self, product_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        try:
            return (
                self._db.query(Review)
                .filter(Review.product_id == product_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting reviews for product {product_id}: {e}")
            return []

    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        try:
            return (
                self._db.query(Review)
                .filter(Review.user_id == user_id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting reviews by user {user_id}: {e}")
            return []

    def get_user_review_for_product(self, user_id: int, product_id: int) -> Optional[Review]:
        try:
            return self._db.query(Review).filter(
                Review.user_id == user_id,
                Review.product_id == product_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user review: {e}")
            return None
