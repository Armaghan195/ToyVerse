from typing import Optional, List
from datetime import datetime
import uuid
import logging

from app.services.base_service import BaseService
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.models.order import Order

logger = logging.getLogger(__name__)

class OrderService(BaseService[Order]):
    def __init__(
        self,
        repository: OrderRepository,
        cart_repository: CartRepository,
        product_repository: ProductRepository
    ):
        super().__init__(repository)
        self._cart_repository = cart_repository
        self._product_repository = product_repository

    def get_by_id(self, id: int) -> Optional[Order]:
        try:
            return self._repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Error getting order: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        try:
            return self._repository.get_all(skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting all orders: {e}")
            return []

    def create(self, data: dict) -> Optional[Order]:
        try:
            if not self._validate(data):
                return None

            order = Order(
                order_number=self._generate_order_number(),
                user_id=data.get('user_id'),
                total=data.get('total'),
                status='pending',
                payment_method=data.get('payment_method', 'COD')
            )

            order.customer_details = data.get('customer_details', {})
            order.items = data.get('items', [])

            created_order = self._repository.create(order)

            if created_order and data.get('clear_cart', False):
                self._cart_repository.clear_user_cart(data['user_id'])

            return created_order

        except Exception as e:
            self._logger.error(f"Error creating order: {e}")
            return None

    def update(self, id: int, data: dict) -> Optional[Order]:
        try:
            return self._repository.update(id, data)
        except Exception as e:
            self._logger.error(f"Error updating order: {e}")
            return None

    def delete(self, id: int) -> bool:
        try:
            return self._repository.delete(id)
        except Exception as e:
            self._logger.error(f"Error deleting order: {e}")
            return False

    def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        try:
            return self._repository.get_by_user_id(user_id, skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting user orders: {e}")
            return []

    def get_by_order_number(self, order_number: str) -> Optional[Order]:
        try:
            return self._repository.get_by_order_number(order_number)
        except Exception as e:
            self._logger.error(f"Error getting order by number: {e}")
            return None

    def update_status(self, order_id: int, status: str) -> Optional[Order]:
        try:
            valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
            if status not in valid_statuses:
                self._logger.warning(f"Invalid order status: {status}")
                return None

            return self._repository.update(order_id, {'status': status})
        except Exception as e:
            self._logger.error(f"Error updating order status: {e}")
            return None

    def create_from_cart(self, user_id: int, customer_details: dict, payment_method: str = 'COD') -> Optional[Order]:
        try:
            cart_items = self._cart_repository.get_by_user_id(user_id)

            if not cart_items:
                self._logger.warning(f"Cart is empty for user {user_id}")
                return None

            order_items = []
            total = 0

            for cart_item in cart_items:
                product = self._product_repository.get_by_id(cart_item.product_id)

                if not product:
                    continue

                if product.stock < cart_item.quantity:
                    self._logger.warning(f"Insufficient stock for product {product.id}")
                    return None

                item_data = {
                    'product_id': product.id,
                    'title': product.title,
                    'price': float(product.price),
                    'quantity': cart_item.quantity,
                    'subtotal': float(product.price) * cart_item.quantity
                }

                order_items.append(item_data)
                total += item_data['subtotal']

                product.decrease_stock(cart_item.quantity)
                self._product_repository.update(product.id, {'stock': product.stock})

            order_data = {
                'user_id': user_id,
                'customer_details': customer_details,
                'items': order_items,
                'total': total,
                'payment_method': payment_method,
                'clear_cart': True
            }

            return self.create(order_data)

        except Exception as e:
            self._logger.error(f"Error creating order from cart: {e}")
            return None

    def _generate_order_number(self) -> str:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{random_suffix}"

    def _validate(self, data: dict) -> bool:
        required_fields = ['user_id', 'total']
        for field in required_fields:
            if field not in data:
                self._logger.warning(f"Missing required field: {field}")
                return False
        return True
