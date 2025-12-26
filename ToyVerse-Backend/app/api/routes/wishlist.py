
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.wishlist_service import WishlistService
from app.schemas.wishlist import WishlistResponse, WishlistCreate, WishlistProductIds

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.get("", response_model=List[WishlistResponse])
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = WishlistService(db)
    wishlist = service.get_user_wishlist(current_user.id)
    return wishlist

@router.get("/product-ids", response_model=WishlistProductIds)
async def get_wishlist_product_ids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = WishlistService(db)
    product_ids = service.get_wishlist_product_ids(current_user.id)
    return {"product_ids": product_ids}

@router.post("/add", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    data: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = WishlistService(db)
    wishlist_item = service.add_to_wishlist(current_user.id, data.product_id)
    return wishlist_item

@router.delete("/remove/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = WishlistService(db)
    service.remove_from_wishlist(current_user.id, product_id)
    return None

@router.get("/check/{product_id}", response_model=dict)
async def check_in_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = WishlistService(db)
    is_wishlisted = service.is_in_wishlist(current_user.id, product_id)
    return {"product_id": product_id, "is_wishlisted": is_wishlisted}

@router.delete("/clear", status_code=status.HTTP_200_OK)
async def clear_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = WishlistService(db)
    count = service.clear_wishlist(current_user.id)
    return {"message": f"Cleared {count} items from wishlist"}
