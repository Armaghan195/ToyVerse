from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.repositories.base_repository import BaseRepository
from app.models.chat_message import ChatMessage

logger = logging.getLogger(__name__)

class ChatRepository(BaseRepository[ChatMessage]):
    def __init__(self, db: Session):
        super().__init__(ChatMessage, db)

    def get_by_id(self, id: int) -> Optional[ChatMessage]:
        try:
            return self._db.query(ChatMessage).filter(ChatMessage.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting chat message by ID {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        try:
            return (
                self._db.query(ChatMessage)
                .order_by(ChatMessage.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting all chat messages: {e}")
            return []

    def create(self, entity: ChatMessage) -> ChatMessage:
        try:
            self._db.add(entity)
            if self._commit():
                self._refresh(entity)
                return entity
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error creating chat message: {e}")
            self._db.rollback()
            return None

    def update(self, id: int, data: Dict[str, Any]) -> Optional[ChatMessage]:
        try:
            message = self.get_by_id(id)
            if message:
                for key, value in data.items():
                    if hasattr(message, key) and key != 'id':
                        setattr(message, key, value)
                if self._commit():
                    self._refresh(message)
                    return message
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error updating chat message {id}: {e}")
            self._db.rollback()
            return None

    def delete(self, id: int) -> bool:
        try:
            message = self.get_by_id(id)
            if message:
                self._db.delete(message)
                return self._commit()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting chat message {id}: {e}")
            self._db.rollback()
            return False

    def get_by_session(self, session_id: str, skip: int = 0, limit: int = 50) -> List[ChatMessage]:
        try:
            return (
                self._db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting chat messages by session: {e}")
            return []

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        try:
            return (
                self._db.query(ChatMessage)
                .filter(ChatMessage.user_id == user_id)
                .order_by(ChatMessage.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting chat messages by user: {e}")
            return []

    def clear_session(self, session_id: str) -> bool:
        try:
            self._db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
            return self._commit()
        except SQLAlchemyError as e:
            logger.error(f"Error clearing session {session_id}: {e}")
            self._db.rollback()
            return False
