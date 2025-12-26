from typing import Optional, List
import logging

from app.services.base_service import BaseService
from app.repositories.review_repository import ReviewRepository
from app.repositories.product_repository import ProductRepository
from app.models.review import Review

logger = logging.getLogger(__name__)

class ReviewService(BaseService[Review]):
    def __init__(self, repository: ReviewRepository, product_repository: ProductRepository):
        super().__init__(repository)
        self._product_repository = product_repository

    def get_by_id(self, id: int) -> Optional[Review]:
        try:
            return self._repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Error getting review: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Review]:
        try:
            return self._repository.get_all(skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting all reviews: {e}")
            return []

    def create(self, data: dict) -> Optional[Review]:
        try:
            if not self._validate(data):
                return None

            existing_review = self._repository.get_user_review_for_product(
                data['user_id'],
                data['product_id']
            )

            if existing_review:
                self._logger.warning("User already reviewed this product")
                return None

            review = Review(
                product_id=data.get('product_id'),
                user_id=data.get('user_id'),
                rating=data.get('rating'),
                text=data.get('text', '')
            )

            created_review = self._repository.create(review)

            if created_review:
                self._update_product_rating(data['product_id'])

            return created_review

        except Exception as e:
            self._logger.error(f"Error creating review: {e}")
            return None

    def update(self, id: int, data: dict) -> Optional[Review]:
        try:
            updated_review = self._repository.update(id, data)

            if updated_review:
                self._update_product_rating(updated_review.product_id)

            return updated_review
        except Exception as e:
            self._logger.error(f"Error updating review: {e}")
            return None

    def delete(self, id: int) -> bool:
        try:
            review = self._repository.get_by_id(id)
            if review:
                product_id = review.product_id
                if self._repository.delete(id):
                    self._update_product_rating(product_id)
                    return True
            return False
        except Exception as e:
            self._logger.error(f"Error deleting review: {e}")
            return False

    def get_product_reviews(self, product_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        try:
            return self._repository.get_by_product_id(product_id, skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting product reviews: {e}")
            return []

    def get_user_reviews(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        try:
            return self._repository.get_by_user_id(user_id, skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting user reviews: {e}")
            return []

    def _update_product_rating(self, product_id: int) -> None:
        try:
            reviews = self._repository.get_by_product_id(product_id, skip=0, limit=1000)

            if not reviews:
                self._product_repository.update(product_id, {'rating': 0})
                return

            total_rating = sum(review.rating for review in reviews)
            average_rating = round(total_rating / len(reviews))

            self._product_repository.update(product_id, {'rating': average_rating})

        except Exception as e:
            self._logger.error(f"Error updating product rating: {e}")

    def _validate(self, data: dict) -> bool:
        required_fields = ['product_id', 'user_id', 'rating']
        for field in required_fields:
            if field not in data:
                self._logger.warning(f"Missing required field: {field}")
                return False

        if not (1 <= data['rating'] <= 5):
            self._logger.warning("Rating must be between 1 and 5")
            return False

        product = self._product_repository.get_by_id(data['product_id'])
        if not product:
            self._logger.warning(f"Product {data['product_id']} not found")
            return False

        return True
