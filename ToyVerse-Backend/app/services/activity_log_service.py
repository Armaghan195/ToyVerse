from typing import Optional, List
import logging

from app.services.base_service import BaseService
from app.repositories.activity_log_repository import ActivityLogRepository
from app.models.activity_log import ActivityLog

logger = logging.getLogger(__name__)

class ActivityLogService(BaseService[ActivityLog]):
    def __init__(self, repository: ActivityLogRepository):
        super().__init__(repository)

    def get_by_id(self, id: int) -> Optional[ActivityLog]:
        try:
            return self._repository.get_by_id(id)
        except Exception as e:
            self._logger.error(f"Error getting activity log: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ActivityLog]:
        try:
            return self._repository.get_all(skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting all activity logs: {e}")
            return []

    def create(self, data: dict) -> Optional[ActivityLog]:
        try:
            if not self._validate(data):
                return None

            log = ActivityLog(
                actor=data.get('actor'),
                action=data.get('action')
            )

            return self._repository.create(log)
        except Exception as e:
            self._logger.error(f"Error creating activity log: {e}")
            return None

    def update(self, id: int, data: dict) -> Optional[ActivityLog]:
        try:
            return self._repository.update(id, data)
        except Exception as e:
            self._logger.error(f"Error updating activity log: {e}")
            return None

    def delete(self, id: int) -> bool:
        try:
            return self._repository.delete(id)
        except Exception as e:
            self._logger.error(f"Error deleting activity log: {e}")
            return False

    def log(self, actor: str, action: str) -> Optional[ActivityLog]:
        try:
            return self._repository.log_activity(actor, action)
        except Exception as e:
            self._logger.error(f"Error logging activity: {e}")
            return None

    def get_by_actor(self, actor: str, skip: int = 0, limit: int = 100) -> List[ActivityLog]:
        try:
            return self._repository.get_by_actor(actor, skip, limit)
        except Exception as e:
            self._logger.error(f"Error getting logs by actor: {e}")
            return []

    def _validate(self, data: dict) -> bool:
        required_fields = ['actor', 'action']
        for field in required_fields:
            if field not in data or not data[field]:
                self._logger.warning(f"Missing required field: {field}")
                return False
        return True
