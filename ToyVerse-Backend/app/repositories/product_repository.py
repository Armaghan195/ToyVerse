
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
import logging

from app.repositories.base_repository import BaseRepository
from app.models.product import Product

logger = logging.getLogger(__name__)

class ProductRepository(BaseRepository[Product]):

    def __init__(self, db: Session):

        super().__init__(Product, db)

    def get_by_id(self, id: int) -> Optional[Product]:

        try:
            return self._db.query(Product).filter(Product.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting product by ID {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:

        try:

            return (
                self._db.query(Product)
                .order_by(Product.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting all products: {e}")
            return []

    def create(self, entity: Product) -> Product:

        try:
            self._db.add(entity)
            if self._commit():
                self._refresh(entity)
                return entity
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error creating product: {e}")
            self._db.rollback()
            return None

    def update(self, id: int, data: Dict[str, Any]) -> Optional[Product]:

        try:
            product = self.get_by_id(id)
            if product:
                for key, value in data.items():
                    if hasattr(product, key) and key != 'id':
                        setattr(product, key, value)
                if self._commit():
                    self._refresh(product)
                    return product
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error updating product {id}: {e}")
            self._db.rollback()
            return None

    def delete(self, id: int) -> bool:

        try:
            product = self.get_by_id(id)
            if product:
                self._db.delete(product)
                return self._commit()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting product {id}: {e}")
            self._db.rollback()
            return False

    def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Product]:

        try:
            return (
                self._db.query(Product)
                .filter(Product.category == category)
                .order_by(Product.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting products by category {category}: {e}")
            return []

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:

        try:
            search_pattern = f"%{query}%"
            return (
                self._db.query(Product)
                .filter(
                    or_(
                        Product.title.ilike(search_pattern),
                        Product.description.ilike(search_pattern)
                    )
                )
                .order_by(Product.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error searching products: {e}")
            return []

    def get_in_stock(self, skip: int = 0, limit: int = 100) -> List[Product]:

        try:
            return (
                self._db.query(Product)
                .filter(Product.stock > 0)
                .order_by(Product.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting in-stock products: {e}")
            return []

    def get_by_rating(self, min_rating: int, skip: int = 0, limit: int = 100) -> List[Product]:

        try:
            return (
                self._db.query(Product)
                .filter(Product.rating >= min_rating)
                .order_by(Product.id)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting products by rating: {e}")
            return []

    def filter_products(
        self,
        category: Optional[str] = None,
        price_max: Optional[float] = None,
        rating: Optional[int] = None,
        in_stock: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:

        try:

            query = self._db.query(Product).order_by(Product.id)

            if category:
                query = query.filter(Product.category == category)
            if price_max:
                query = query.filter(Product.price <= price_max)
            if rating:
                query = query.filter(Product.rating >= rating)
            if in_stock:
                query = query.filter(Product.stock > 0)
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    or_(
                        Product.title.ilike(search_pattern),
                        Product.description.ilike(search_pattern)
                    )
                )

            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error filtering products: {e}")
            return []
