from sqlalchemy import Column, String, Text
from app.models.base import BaseModel

class ActivityLog(BaseModel):
    __tablename__ = "activity_logs"

    actor = Column(String(100), nullable=False)
    action = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<ActivityLog(id={self.id}, actor={self.actor}, action={self.action[:50]})>"
