
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import jwt_handler
from app.models.user import User, Admin
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.interaction_repository import InteractionRepository
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.review_service import ReviewService
from app.services.activity_log_service import ActivityLogService
from app.services.chatbot_service import ChatbotService
from app.services.recommendation_service import RecommendationService

security = HTTPBearer()

def get_database() -> Session:

    return Depends(get_db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:

    return UserRepository(db)

def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:

    return ProductRepository(db)

def get_cart_repository(db: Session = Depends(get_db)) -> CartRepository:
    return CartRepository(db)

def get_order_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)

def get_review_repository(db: Session = Depends(get_db)) -> ReviewRepository:
    return ReviewRepository(db)

def get_activity_log_repository(db: Session = Depends(get_db)) -> ActivityLogRepository:
    return ActivityLogRepository(db)

def get_chat_repository(db: Session = Depends(get_db)) -> ChatRepository:
    return ChatRepository(db)

def get_interaction_repository(db: Session = Depends(get_db)) -> InteractionRepository:
    return InteractionRepository(db)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:

    return AuthService(user_repo)

def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository)
) -> ProductService:

    return ProductService(product_repo)

def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    product_repo: ProductRepository = Depends(get_product_repository)
) -> CartService:
    return CartService(cart_repo, product_repo)

def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    cart_repo: CartRepository = Depends(get_cart_repository),
    product_repo: ProductRepository = Depends(get_product_repository)
) -> OrderService:
    return OrderService(order_repo, cart_repo, product_repo)

def get_review_service(
    review_repo: ReviewRepository = Depends(get_review_repository),
    product_repo: ProductRepository = Depends(get_product_repository)
) -> ReviewService:
    return ReviewService(review_repo, product_repo)

def get_activity_log_service(
    log_repo: ActivityLogRepository = Depends(get_activity_log_repository)
) -> ActivityLogService:
    return ActivityLogService(log_repo)

def get_chatbot_service(
    chat_repo: ChatRepository = Depends(get_chat_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    order_repo: OrderRepository = Depends(get_order_repository)
) -> ChatbotService:
    return ChatbotService(chat_repo, product_repo, order_repo)

def get_recommendation_service(
    interaction_repo: InteractionRepository = Depends(get_interaction_repository),
    product_repo: ProductRepository = Depends(get_product_repository)
) -> RecommendationService:
    return RecommendationService(interaction_repo, product_repo)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:

    token = credentials.credentials

    user = auth_service.get_user_by_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:

    if not credentials:
        return None

    token = credentials.credentials
    user = auth_service.get_user_by_token(token)
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:

    return current_user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> Admin:

    if not isinstance(current_user, Admin) and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return current_user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:

    if not credentials:
        return None

    token = credentials.credentials
    user = auth_service.get_user_by_token(token)

    return user
