
from typing import Optional
from fastapi import APIRouter, Depends, Request
from app.models.user import User
from app.services.recommendation_service import RecommendationService
from app.api.dependencies import get_current_user_optional, get_recommendation_service
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("")
async def get_recommendations(
    request: Request,
    type: str = 'all',
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):

    user_id = current_user.id if current_user else None
    session_id = request.headers.get('X-Session-ID') or request.client.host

    recommendations = recommendation_service.get_recommendations_for_user(
        user_id=user_id,
        session_id=session_id,
        rec_type=type,
        limit=limit
    )

    return recommendations

@router.post("/track")
async def track_interaction(
    request: Request,
    product_id: int,
    interaction_type: str = 'view',
    current_user: Optional[User] = Depends(get_current_user_optional),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):

    user_id = current_user.id if current_user else None
    session_id = request.headers.get('X-Session-ID') or request.client.host
    user_agent = request.headers.get('User-Agent')
    ip_address = request.client.host

    interaction = recommendation_service.track_interaction(
        product_id=product_id,
        interaction_type=interaction_type,
        user_id=user_id,
        session_id=session_id,
        user_agent=user_agent,
        ip_address=ip_address
    )

    return {
        "message": "Interaction tracked successfully",
        "interaction": interaction.to_dict()
    }

@router.get("/product/{product_id}")
async def get_product_recommendations(
    product_id: int,
    limit: int = 6,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):

    recommendations = recommendation_service.get_product_recommendations(
        product_id=product_id,
        limit=limit
    )

    return recommendations
