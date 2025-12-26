from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.services.review_service import ReviewService
from app.models.user import User
from app.api.dependencies import get_review_service, get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.get("/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    review_service: ReviewService = Depends(get_review_service)
):
    reviews = review_service.get_product_reviews(product_id, skip, limit)

    return [
        ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            user_id=review.user_id,
            rating=review.rating,
            text=review.text,
            created_at=review.created_at,
            user={
                'id': review.user.id,
                'username': review.user.username
            } if review.user else None
        )
        for review in reviews
    ]

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.create({
        'product_id': review_data.product_id,
        'user_id': current_user.id,
        'rating': review_data.rating,
        'text': review_data.text or ''
    })

    if not review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create review (already reviewed or product not found)"
        )

    return ReviewResponse(
        id=review.id,
        product_id=review.product_id,
        user_id=review.user_id,
        rating=review.rating,
        text=review.text,
        created_at=review.created_at,
        user={
            'id': current_user.id,
            'username': current_user.username
        }
    )

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    update_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.get_by_id(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this review"
        )

    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    updated_review = review_service.update(review_id, update_dict)

    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update review"
        )

    return ReviewResponse(
        id=updated_review.id,
        product_id=updated_review.product_id,
        user_id=updated_review.user_id,
        rating=updated_review.rating,
        text=updated_review.text,
        created_at=updated_review.created_at,
        user={
            'id': current_user.id,
            'username': current_user.username
        }
    )

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    review = review_service.get_by_id(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    if review.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )

    if not review_service.delete(review_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete review"
        )
