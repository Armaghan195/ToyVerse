
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from decimal import Decimal

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService
from app.models.user import User, Admin
from app.api.dependencies import get_product_service, get_current_user, get_current_admin

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    price_max: Optional[Decimal] = Query(None, description="Maximum price filter"),
    rating: Optional[int] = Query(None, ge=0, le=5, description="Minimum rating filter"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    in_stock: Optional[bool] = Query(None, description="Filter in-stock products only"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    product_service: ProductService = Depends(get_product_service)
) -> List[ProductResponse]:

    if any([category, price_max, rating, search, in_stock is not None]):
        products = product_service.filter_products(
            category=category,
            price_max=price_max,
            rating=rating,
            in_stock=in_stock,
            search=search,
            skip=skip,
            limit=limit
        )
    else:

        products = product_service.get_all(skip=skip, limit=limit)

    return [
        ProductResponse(
            id=p.id,
            title=p.title,
            price=p.price,
            category=p.category,
            stock=p.stock,
            rating=p.rating,
            icon=p.icon,
            description=p.description,
            detailed_description=p.detailed_description,
            images=p.images,
            created_at=p.created_at,
            updated_at=p.updated_at,
            is_in_stock=p.is_in_stock,
            formatted_price=p.formatted_price
        )
        for p in products
    ]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
) -> ProductResponse:

    product = product_service.get_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    return ProductResponse(
        id=product.id,
        title=product.title,
        price=product.price,
        category=product.category,
        stock=product.stock,
        rating=product.rating,
        icon=product.icon,
        description=product.description,
        detailed_description=product.detailed_description,
        images=product.images,
        created_at=product.created_at,
        updated_at=product.updated_at,
        is_in_stock=product.is_in_stock,
        formatted_price=product.formatted_price
    )

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
    current_admin: Admin = Depends(get_current_admin)
) -> ProductResponse:

    product_dict = product_data.model_dump()

    product = product_service.create(product_dict)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create product"
        )

    return ProductResponse(
        id=product.id,
        title=product.title,
        price=product.price,
        category=product.category,
        stock=product.stock,
        rating=product.rating,
        icon=product.icon,
        description=product.description,
        detailed_description=product.detailed_description,
        images=product.images,
        created_at=product.created_at,
        updated_at=product.updated_at,
        is_in_stock=product.is_in_stock,
        formatted_price=product.formatted_price
    )

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
    current_admin: Admin = Depends(get_current_admin)
) -> ProductResponse:

    update_dict = product_data.model_dump(exclude_unset=True)

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    product = product_service.update(product_id, update_dict)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    return ProductResponse(
        id=product.id,
        title=product.title,
        price=product.price,
        category=product.category,
        stock=product.stock,
        rating=product.rating,
        icon=product.icon,
        description=product.description,
        detailed_description=product.detailed_description,
        images=product.images,
        created_at=product.created_at,
        updated_at=product.updated_at,
        is_in_stock=product.is_in_stock,
        formatted_price=product.formatted_price
    )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
    current_admin: Admin = Depends(get_current_admin)
) -> None:

    success = product_service.delete(product_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
