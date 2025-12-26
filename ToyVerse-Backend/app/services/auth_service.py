
from typing import Optional, Dict, Any
from datetime import timedelta
import logging

from app.services.base_service import BaseService
from app.repositories.user_repository import UserRepository
from app.models.user import User, create_user
from app.core.security import password_handler, jwt_handler, create_access_token
from app.schemas.user import UserCreate, Token, UserResponse

logger = logging.getLogger(__name__)

class AuthService(BaseService[User]):

    def __init__(self, repository: UserRepository):

        super().__init__(repository)

    def get_by_id(self, id: int) -> Optional[User]:

        try:
            return self._repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Error getting user by ID: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:

        try:
            return self._repository.get_all(skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting all users: {e}")
            return []

    def create(self, data: dict) -> Optional[User]:

        return None

    def update(self, id: int, data: dict) -> Optional[User]:

        try:
            if not self._validate(data):
                return None
            return self._repository.update(id, data)
        except Exception as e:
            self._logger.error(f"Error updating user: {e}")
            return None

    def delete(self, id: int) -> bool:

        try:
            return self._repository.delete(id)
        except Exception as e:
            self._logger.error(f"Error deleting user: {e}")
            return False

    def register(self, user_data: UserCreate) -> Optional[User]:

        try:

            if self._repository.username_exists(user_data.username):
                self._logger.warning(f"Username already exists: {user_data.username}")
                return None

            if self._repository.email_exists(user_data.email):
                self._logger.warning(f"Email already exists: {user_data.email}")
                return None

            password_hash = password_handler.hash_password(user_data.password)

            user = create_user(
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                role=user_data.role
            )

            if user_data.full_name:
                user.full_name = user_data.full_name

            created_user = self._repository.create(user)

            if created_user:
                self._log_operation("User registered", created_user.id)
                return created_user

            return None

        except Exception as e:
            self._logger.error(f"Error registering user: {e}")
            return None

    def authenticate(self, username: str, password: str) -> Optional[User]:

        try:

            user = self._repository.get_by_username(username)
            if not user:
                user = self._repository.get_by_email(username)

            if not user:
                self._logger.warning(f"User not found: {username}")
                return None

            if not password_handler.verify_password(password, user.password_hash):
                self._logger.warning(f"Invalid password for user: {username}")
                return None

            self._log_operation("User authenticated", user.id)
            return user

        except Exception as e:
            self._logger.error(f"Error authenticating user: {e}")
            return None

    def create_token(self, user: User) -> str:

        try:

            token_data = {
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            }

            access_token = create_access_token(token_data)
            return access_token

        except Exception as e:
            self._logger.error(f"Error creating token: {e}")
            return None

    def get_user_by_token(self, token: str) -> Optional[User]:

        try:

            payload = jwt_handler.verify_token(token)

            if not payload:
                return None

            username = payload.get("sub")
            if not username:
                return None

            user = self._repository.get_by_username(username)
            return user

        except Exception as e:
            self._logger.error(f"Error getting user from token: {e}")
            return None

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:

        try:
            user = self._repository.get_by_id(user_id)
            if not user:
                return False

            if not password_handler.verify_password(old_password, user.password_hash):
                self._logger.warning(f"Invalid old password for user {user_id}")
                return False

            new_password_hash = password_handler.hash_password(new_password)

            updated_user = self._repository.update(user_id, {"password_hash": new_password_hash})

            if updated_user:
                self._log_operation("Password changed", user_id)
                return True

            return False

        except Exception as e:
            self._logger.error(f"Error changing password: {e}")
            return False
