from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from decimal import Decimal

from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
from app.services.cart_service import CartService
from app.models.user import User
from app.api.dependencies import get_cart_service, get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    cart_items = cart_service.get_user_cart(current_user.id)

    items_response = []
    total = Decimal('0')

    for item in cart_items:
        item_data = CartItemResponse(
            id=item.id,
            user_id=item.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            created_at=item.created_at,
            product={
                'id': item.product.id,
                'title': item.product.title,
                'price': float(item.product.price),
                'icon': item.product.icon,
                'stock': item.product.stock,
                'images': item.product.images
            } if item.product else None,
            subtotal=item.subtotal
        )
        items_response.append(item_data)
        total += Decimal(str(item.subtotal))

    return CartResponse(
        items=items_response,
        total=total,
        item_count=len(items_response)
    )

@router.post("/add", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    cart_item = cart_service.add_to_cart(
        user_id=current_user.id,
        product_id=item_data.product_id,
        quantity=item_data.quantity
    )

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add item to cart (product not found or insufficient stock)"
        )

    return CartItemResponse(
        id=cart_item.id,
        user_id=cart_item.user_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        created_at=cart_item.created_at,
        product={
            'id': cart_item.product.id,
            'title': cart_item.product.title,
            'price': float(cart_item.product.price),
            'icon': cart_item.product.icon,
            'stock': cart_item.product.stock
        } if cart_item.product else None,
        subtotal=cart_item.subtotal
    )

@router.put("/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    update_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    cart_item = cart_service.get_by_id(item_id)

    if not cart_item or cart_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    updated_item = cart_service.update_quantity(item_id, update_data.quantity)

    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update cart item (insufficient stock)"
        )

    return CartItemResponse(
        id=updated_item.id,
        user_id=updated_item.user_id,
        product_id=updated_item.product_id,
        quantity=updated_item.quantity,
        created_at=updated_item.created_at,
        product={
            'id': updated_item.product.id,
            'title': updated_item.product.title,
            'price': float(updated_item.product.price),
            'icon': updated_item.product.icon,
            'stock': updated_item.product.stock
        } if updated_item.product else None,
        subtotal=updated_item.subtotal
    )

@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    if not cart_service.clear_cart(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to clear cart"
        )

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    cart_item = cart_service.get_by_id(item_id)

    if not cart_item or cart_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    if not cart_service.delete(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove item from cart"
        )


