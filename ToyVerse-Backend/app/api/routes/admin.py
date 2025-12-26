from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.schemas.order import OrderResponse
from app.services.order_service import OrderService
from app.services.activity_log_service import ActivityLogService
from app.models.user import Admin
from app.api.dependencies import get_order_service, get_activity_log_service, get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/orders", response_model=List[OrderResponse])
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    order_status: Optional[str] = Query(None, description="Filter by status"),
    current_admin: Admin = Depends(get_current_admin),
    order_service: OrderService = Depends(get_order_service)
):
    if order_status:
        orders = order_service._repository.get_by_status(order_status, skip, limit)
    else:
        orders = order_service.get_all(skip, limit)

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

@router.get("/logs")
async def get_activity_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    actor: Optional[str] = Query(None, description="Filter by actor"),
    current_admin: Admin = Depends(get_current_admin),
    log_service: ActivityLogService = Depends(get_activity_log_service)
):
    if actor:
        logs = log_service.get_by_actor(actor, skip, limit)
    else:
        logs = log_service.get_all(skip, limit)

    return [
        {
            'id': log.id,
            'actor': log.actor,
            'action': log.action,
            'timestamp': log.created_at
        }
        for log in logs
    ]

@router.post("/logs")
async def create_activity_log(
    actor: str,
    action: str,
    current_admin: Admin = Depends(get_current_admin),
    log_service: ActivityLogService = Depends(get_activity_log_service)
):
    log = log_service.log(actor, action)

    if not log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create activity log"
        )

    return {
        'id': log.id,
        'actor': log.actor,
        'action': log.action,
        'timestamp': log.created_at
    }
