from typing import Optional, List
import logging

from app.services.base_service import BaseService
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.models.cart import CartItem

logger = logging.getLogger(__name__)

class CartService(BaseService[CartItem]):
    def __init__(self, repository: CartRepository, product_repository: ProductRepository):
        super().__init__(repository)
        self._product_repository = product_repository

    def get_by_id(self, id: int) -> Optional[CartItem]:
        try:
            return self._repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Error getting cart item: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[CartItem]:
        try:
            return self._repository.get_all(skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting all cart items: {e}")
            return []

    def create(self, data: dict) -> Optional[CartItem]:
        try:
            if not self._validate(data):
                return None

            cart_item = CartItem(
                user_id=data.get('user_id'),
                product_id=data.get('product_id'),
                quantity=data.get('quantity', 1)
            )

            return self._repository.create(cart_item)
        except Exception as e:
            self._logger.error(f"Error creating cart item: {e}")
            return None

    def update(self, id: int, data: dict) -> Optional[CartItem]:
        try:
            return self._repository.update(id, data)
        except Exception as e:
            self._logger.error(f"Error updating cart item: {e}")
            return None

    def delete(self, id: int) -> bool:
        try:
            return self._repository.delete(id)
        except Exception as e:
            self._logger.error(f"Error deleting cart item: {e}")
            return False

    def get_user_cart(self, user_id: int) -> List[CartItem]:
        try:
            return self._repository.get_by_user_id(user_id)
        except Exception as e:
            self._logger.error(f"Error getting user cart: {e}")
            return []

    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> Optional[CartItem]:
        try:
            product = self._product_repository.get_by_id(product_id)
            if not product:
                self._logger.warning(f"Product {product_id} not found")
                return None

            if product.stock < quantity:
                self._logger.warning(f"Insufficient stock for product {product_id}")
                return None

            existing_item = self._repository.get_by_user_and_product(user_id, product_id)

            if existing_item:
                new_quantity = existing_item.quantity + quantity
                if product.stock < new_quantity:
                    self._logger.warning(f"Insufficient stock for product {product_id}")
                    return None
                return self._repository.update(existing_item.id, {'quantity': new_quantity})
            else:
                cart_item = CartItem(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity
                )
                return self._repository.create(cart_item)

        except Exception as e:
            self._logger.error(f"Error adding to cart: {e}")
            return None

    def update_quantity(self, cart_item_id: int, quantity: int) -> Optional[CartItem]:
        try:
            cart_item = self._repository.get_by_id(cart_item_id)
            if not cart_item:
                return None

            product = self._product_repository.get_by_id(cart_item.product_id)
            if not product or product.stock < quantity:
                return None

            return self._repository.update(cart_item_id, {'quantity': quantity})
        except Exception as e:
            self._logger.error(f"Error updating quantity: {e}")
            return None

    def clear_cart(self, user_id: int) -> bool:
        try:
            return self._repository.clear_user_cart(user_id)
        except Exception as e:
            self._logger.error(f"Error clearing cart: {e}")
            return False

    def _validate(self, data: dict) -> bool:
        if 'user_id' not in data or 'product_id' not in data:
            return False
        if 'quantity' in data and data['quantity'] <= 0:
            return False
        return True
