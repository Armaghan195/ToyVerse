
from typing import Optional, List, Dict, Any
from decimal import Decimal
import logging

from app.services.base_service import BaseService
from app.repositories.product_repository import ProductRepository
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)

class ProductService(BaseService[Product]):

    def __init__(self, repository: ProductRepository):

        super().__init__(repository)

    def get_by_id(self, id: int) -> Optional[Product]:

        try:
            product = self._repository.get_by_id(id)
            if product:
                self._log_operation("Product retrieved", id)
            return product
        except Exception as e:
            self._logger.error(f"Error getting product: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:

        try:
            products = self._repository.get_all(skip, limit)
            self._log_operation(f"Retrieved {len(products)} products")
            return products
        except Exception as e:
            self._logger.error(f"Error getting all products: {e}")
            return []

    def create(self, data: dict) -> Optional[Product]:

        try:

            if not self._validate(data):
                return None

            product = Product(
                title=data.get('title'),
                price=data.get('price'),
                category=data.get('category'),
                stock=data.get('stock', 0),
                rating=data.get('rating', 0),
                icon=data.get('icon'),
                description=data.get('description'),
                detailed_description=data.get('detailed_description')
            )

            if 'images' in data:
                product.images = data['images']

            created_product = self._repository.create(product)

            if created_product:
                self._log_operation("Product created", created_product.id)
                return created_product

            return None

        except Exception as e:
            self._logger.error(f"Error creating product: {e}")
            return None

    def update(self, id: int, data: dict) -> Optional[Product]:

        try:

            if not self._repository.exists(id):
                self._logger.warning(f"Product not found: {id}")
                return None

            if 'images' in data and isinstance(data['images'], list):
                import json
                data['images_json'] = json.dumps(data['images'])
                del data['images']

            updated_product = self._repository.update(id, data)

            if updated_product:
                self._log_operation("Product updated", id)
                return updated_product

            return None

        except Exception as e:
            self._logger.error(f"Error updating product: {e}")
            return None

    def delete(self, id: int) -> bool:

        try:
            if self._repository.delete(id):
                self._log_operation("Product deleted", id)
                return True
            return False
        except Exception as e:
            self._logger.error(f"Error deleting product: {e}")
            return False

    def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Product]:

        try:
            products = self._repository.get_by_category(category, skip, limit)
            self._log_operation(f"Retrieved {len(products)} products in category {category}")
            return products
        except Exception as e:
            self._logger.error(f"Error getting products by category: {e}")
            return []

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:

        try:
            products = self._repository.search(query, skip, limit)
            self._log_operation(f"Search '{query}' returned {len(products)} products")
            return products
        except Exception as e:
            self._logger.error(f"Error searching products: {e}")
            return []

    def filter_products(
        self,
        category: Optional[str] = None,
        price_max: Optional[Decimal] = None,
        rating: Optional[int] = None,
        in_stock: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:

        try:
            products = self._repository.filter_products(
                category=category,
                price_max=float(price_max) if price_max else None,
                rating=rating,
                in_stock=in_stock,
                search=search,
                skip=skip,
                limit=limit
            )

            self._log_operation(f"Filter returned {len(products)} products")
            return products

        except Exception as e:
            self._logger.error(f"Error filtering products: {e}")
            return []

    def update_stock(self, product_id: int, quantity_change: int) -> Optional[Product]:

        try:
            product = self._repository.get_by_id(product_id)
            if not product:
                return None

            new_stock = product.stock + quantity_change

            if new_stock < 0:
                self._logger.warning(f"Insufficient stock for product {product_id}")
                return None

            return self._repository.update(product_id, {"stock": new_stock})

        except Exception as e:
            self._logger.error(f"Error updating stock: {e}")
            return None

    def _validate(self, data: dict) -> bool:

        required_fields = ['title', 'price', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                self._logger.warning(f"Missing required field: {field}")
                return False

        if data['price'] <= 0:
            self._logger.warning("Price must be positive")
            return False

        if 'stock' in data and data['stock'] < 0:
            self._logger.warning("Stock cannot be negative")
            return False

        if 'rating' in data and (data['rating'] < 0 or data['rating'] > 5):
            self._logger.warning("Rating must be between 0 and 5")
            return False

        return True
