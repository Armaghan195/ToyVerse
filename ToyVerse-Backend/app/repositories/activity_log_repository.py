from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.repositories.base_repository import BaseRepository
from app.models.activity_log import ActivityLog

logger = logging.getLogger(__name__)

class ActivityLogRepository(BaseRepository[ActivityLog]):
    def __init__(self, db: Session):
        super().__init__(ActivityLog, db)

    def get_by_id(self, id: int) -> Optional[ActivityLog]:
        try:
            return self._db.query(ActivityLog).filter(ActivityLog.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting activity log by ID {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ActivityLog]:
        try:
            return (
                self._db.query(ActivityLog)
                .order_by(ActivityLog.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting all activity logs: {e}")
            return []

    def create(self, entity: ActivityLog) -> ActivityLog:
        try:
            self._db.add(entity)
            if self._commit():
                self._refresh(entity)
                return entity
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error creating activity log: {e}")
            self._db.rollback()
            return None

    def update(self, id: int, data: Dict[str, Any]) -> Optional[ActivityLog]:
        try:
            log = self.get_by_id(id)
            if log:
                for key, value in data.items():
                    if hasattr(log, key) and key != 'id':
                        setattr(log, key, value)
                if self._commit():
                    self._refresh(log)
                    return log
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error updating activity log {id}: {e}")
            self._db.rollback()
            return None

    def delete(self, id: int) -> bool:
        try:
            log = self.get_by_id(id)
            if log:
                self._db.delete(log)
                return self._commit()
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting activity log {id}: {e}")
            self._db.rollback()
            return False

    def get_by_actor(self, actor: str, skip: int = 0, limit: int = 100) -> List[ActivityLog]:
        try:
            return (
                self._db.query(ActivityLog)
                .filter(ActivityLog.actor == actor)
                .order_by(ActivityLog.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error getting activity logs by actor: {e}")
            return []

    def log_activity(self, actor: str, action: str) -> ActivityLog:
        log = ActivityLog(actor=actor, action=action)
        return self.create(log)
