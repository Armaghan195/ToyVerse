
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Type, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):

    def __init__(self, model: Type[T], db: Session):

        self._model = model
        self._db = db

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:

        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:

        pass

    @abstractmethod
    def create(self, entity: T) -> T:

        pass

    @abstractmethod
    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:

        pass

    @abstractmethod
    def delete(self, id: int) -> bool:

        pass

    def exists(self, id: int) -> bool:

        try:
            entity = self._db.query(self._model).filter(self._model.id == id).first()
            return entity is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence: {e}")
            return False

    def count(self) -> int:

        try:
            return self._db.query(self._model).count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting entities: {e}")
            return 0

    def _commit(self) -> bool:

        try:
            self._db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database commit error: {e}")
            self._db.rollback()
            return False

    def _refresh(self, entity: T) -> T:

        self._db.refresh(entity)
        return entity
