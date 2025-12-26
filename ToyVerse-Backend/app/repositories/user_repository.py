
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.repositories.base_repository import BaseRepository
from app.models.user import User, Admin, Customer

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):

    def __init__(self, db: Session):

        super().__init__(User, db)

    def get_by_id(self, id: int) -> Optional[User]:

        try:
            return self._db.query(User).filter(User.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by ID {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:

        try:
            return self._db.query(User).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def create(self, entity: User) -> User:

        try:
            self._db.add(entity)
            if self._commit():
                self._refresh(entity)
                return entity
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {e}")
            self._db.rollback()
            return None

    def update(self, id: int, data: Dict[str, Any]) -> Optional[User]:

        try:
            user = self.get_by_id(id)
            if user:
                for key, value in data.items():
                    if hasattr(user, key) and key != 'id':
                        setattr(user, key, value)
                if self._commit():
                    self._refresh(user)
                    return user
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error updating user {id}: {e}")
            self._db.rollback()
            return None

    def delete(self, id: int) -> bool:

        try:
            user = self.get_by_id(id)
            if user:
                self._db.delete(user)
                return self._commit()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting user {id}: {e}")
            self._db.rollback()
            return False

    def get_by_username(self, username: str) -> Optional[User]:

        try:
            return self._db.query(User).filter(User.username == username).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None

    def get_by_email(self, email: str) -> Optional[User]:

        try:
            return self._db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    def username_exists(self, username: str) -> bool:

        try:
            return self._db.query(User).filter(User.username == username).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking username existence: {e}")
            return False

    def email_exists(self, email: str) -> bool:

        try:
            return self._db.query(User).filter(User.email == email).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking email existence: {e}")
            return False

    def get_admins(self) -> List[Admin]:

        try:
            return self._db.query(Admin).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting admins: {e}")
            return []

    def get_customers(self) -> List[Customer]:

        try:
            return self._db.query(Customer).all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting customers: {e}")
            return []
