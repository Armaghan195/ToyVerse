
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.wishlist import Wishlist
from app.models.product import Product
from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.product_repository import ProductRepository

class WishlistService:

    def __init__(self, db: Session):
        self.repository = WishlistRepository(db)
        self.product_repository = ProductRepository(db)
        self.db = db

    def get_user_wishlist(self, user_id: int) -> List[Wishlist]:

        return self.repository.get_user_wishlist(user_id)

    def add_to_wishlist(self, user_id: int, product_id: int) -> Wishlist:

        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )

        if self.repository.is_in_wishlist(user_id, product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already in your wishlist"
            )

        wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
        self.repository.create(wishlist_item)

        self.db.refresh(wishlist_item)
        return wishlist_item

    def remove_from_wishlist(self, user_id: int, product_id: int) -> bool:

        deleted = self.repository.delete_by_user_and_product(user_id, product_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in your wishlist"
            )
        return True

    def is_in_wishlist(self, user_id: int, product_id: int) -> bool:

        return self.repository.is_in_wishlist(user_id, product_id)

    def get_wishlist_product_ids(self, user_id: int) -> List[int]:

        return self.repository.get_wishlist_product_ids(user_id)

    def clear_wishlist(self, user_id: int) -> int:

        items = self.repository.get_user_wishlist(user_id)
        count = len(items)

        for item in items:
            self.repository.delete(item.id)

        return count
