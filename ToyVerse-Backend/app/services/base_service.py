
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
import logging

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseService(ABC, Generic[T]):

    def __init__(self, repository: BaseRepository[T]):

        self._repository = repository
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:

        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:

        pass

    @abstractmethod
    def create(self, data: dict) -> Optional[T]:

        pass

    @abstractmethod
    def update(self, id: int, data: dict) -> Optional[T]:

        pass

    @abstractmethod
    def delete(self, id: int) -> bool:

        pass

    def _validate(self, data: dict) -> bool:

        return True

    def _log_operation(self, operation: str, entity_id: Optional[int] = None) -> None:

        if entity_id:
            self._logger.info(f"{operation} - Entity ID: {entity_id}")
        else:
            self._logger.info(f"{operation}")

    def exists(self, id: int) -> bool:

        try:
            return self._repository.exists(id)
        except Exception as e:
            self._logger.error(f"Error checking existence: {e}")
            return False

    def count(self) -> int:

        try:
            return self._repository.count()
        except Exception as e:
            self._logger.error(f"Error counting entities: {e}")
            return 0
