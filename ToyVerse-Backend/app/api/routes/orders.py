from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.services.order_service import OrderService
from app.models.user import User, Admin
from app.api.dependencies import get_order_service, get_current_user, get_current_admin

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    customer_details = order_data.customer_details.model_dump()

    order = order_service.create_from_cart(
        user_id=current_user.id,
        customer_details=customer_details,
        payment_method=order_data.payment_method
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create order (cart empty or insufficient stock)"
        )

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        customer_details=order.customer_details,
        items=order.items,
        total=order.total,
        status=order.status,
        payment_method=order.payment_method,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@router.get("", response_model=List[OrderResponse])
async def get_user_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    orders = order_service.get_user_orders(current_user.id, skip, limit)

    return [
        OrderResponse(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            customer_details=order.customer_details,
            items=order.items,
            total=order.total,
            status=order.status,
            payment_method=order.payment_method,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        for order in orders
    ]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service)
):
    order = order_service.get_by_id(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        customer_details=order.customer_details,
        items=order.items,
        total=order.total,
        status=order.status,
        payment_method=order.payment_method,
        created_at=order.created_at,
        updated_at=order.updated_at
    )

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    update_data: OrderUpdate,
    current_admin: Admin = Depends(get_current_admin),
    order_service: OrderService = Depends(get_order_service)
):
    if not update_data.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required"
        )

    order = order_service.update_status(order_id, update_data.status)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or invalid status"
        )

    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        customer_details=order.customer_details,
        items=order.items,
        total=order.total,
        status=order.status,
        payment_method=order.payment_method,
        created_at=order.created_at,
        updated_at=order.updated_at
    )
