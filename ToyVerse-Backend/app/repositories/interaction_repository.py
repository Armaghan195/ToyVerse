
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product_interaction import ProductInteraction
from app.repositories.base_repository import BaseRepository

class InteractionRepository(BaseRepository[ProductInteraction]):

    def __init__(self, db: Session):
        super().__init__(db, ProductInteraction)

    def get_by_id(self, interaction_id: int) -> Optional[ProductInteraction]:

        return self._db.query(self._model).filter(self._model.id == interaction_id).first()

    def create(self, interaction: ProductInteraction) -> ProductInteraction:

        self._db.add(interaction)
        self._db.commit()
        self._db.refresh(interaction)
        return interaction

    def get_user_interactions(
        self,
        user_id: int,
        interaction_type: Optional[str] = None,
        limit: int = 100
    ) -> List[ProductInteraction]:

        query = self._db.query(self._model).filter(self._model.user_id == user_id)

        if interaction_type:
            query = query.filter(self._model.interaction_type == interaction_type)

        return query.order_by(self._model.timestamp.desc()).limit(limit).all()

    def get_product_interactions(
        self,
        product_id: int,
        interaction_type: Optional[str] = None,
        limit: int = 100
    ) -> List[ProductInteraction]:

        query = self._db.query(self._model).filter(self._model.product_id == product_id)

        if interaction_type:
            query = query.filter(self._model.interaction_type == interaction_type)

        return query.order_by(self._model.timestamp.desc()).limit(limit).all()

    def get_session_interactions(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ProductInteraction]:

        return (
            self._db.query(self._model)
            .filter(self._model.session_id == session_id)
            .order_by(self._model.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_popular_products(self, limit: int = 10) -> List[dict]:

        from sqlalchemy import func

        results = (
            self._db.query(
                self._model.product_id,
                func.count(self._model.id).label('interaction_count')
            )
            .group_by(self._model.product_id)
            .order_by(func.count(self._model.id).desc())
            .limit(limit)
            .all()
        )

        return [{'product_id': r[0], 'count': r[1]} for r in results]

    def get_related_products(self, product_id: int, limit: int = 5) -> List[int]:

        from sqlalchemy import func, and_

        user_ids_subquery = (
            self._db.query(self._model.user_id)
            .filter(
                and_(
                    self._model.product_id == product_id,
                    self._model.user_id.isnot(None)
                )
            )
            .subquery()
        )

        results = (
            self._db.query(
                self._model.product_id,
                func.count(self._model.id).label('view_count')
            )
            .filter(
                and_(
                    self._model.user_id.in_(user_ids_subquery),
                    self._model.product_id != product_id
                )
            )
            .group_by(self._model.product_id)
            .order_by(func.count(self._model.id).desc())
            .limit(limit)
            .all()
        )

        return [r[0] for r in results]
