
from typing import List, Optional, Dict
from collections import defaultdict, Counter
from app.models.product import Product
from app.models.product_interaction import ProductInteraction
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.product_repository import ProductRepository

class RecommendationService:

    def __init__(
        self,
        interaction_repo: InteractionRepository,
        product_repo: ProductRepository
    ):
        self._interaction_repo = interaction_repo
        self._product_repo = product_repo

    def get_recommendations_for_user(
        self,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        rec_type: str = 'all',
        limit: int = 20
    ) -> List[Dict]:

        recommendations = []

        if user_id:
            interactions = self._interaction_repo.get_user_interactions(user_id, limit=50)
        elif session_id:
            interactions = self._interaction_repo.get_session_interactions(session_id, limit=50)
        else:

            return self._get_popular_products(limit)

        if not interactions:
            return self._get_popular_products(limit)

        viewed_product_ids = list(set([i.product_id for i in interactions]))

        viewed_products = []
        for pid in viewed_product_ids:
            product = self._product_repo.get_by_id(pid)
            if product:
                viewed_products.append(product)

        if rec_type == 'all' or rec_type == 'category':

            category_recs = self._get_category_based_recommendations(
                viewed_products,
                viewed_product_ids,
                limit=limit // 2
            )
            recommendations.extend(category_recs)

        if rec_type == 'all' or rec_type == 'viewed':

            collab_recs = self._get_collaborative_recommendations(
                viewed_product_ids,
                limit=limit // 2
            )
            recommendations.extend(collab_recs)

        if rec_type == 'all' or rec_type == 'popular':

            popular_recs = self._get_popular_products(limit=10)

            popular_recs = [p for p in popular_recs if p['id'] not in viewed_product_ids]
            recommendations.extend(popular_recs)

        seen = set()
        unique_recs = []
        for rec in recommendations:
            if rec['id'] not in seen and rec['id'] not in viewed_product_ids:
                seen.add(rec['id'])
                unique_recs.append(rec)

        return unique_recs[:limit]

    def _get_category_based_recommendations(
        self,
        viewed_products: List[Product],
        exclude_ids: List[int],
        limit: int = 10
    ) -> List[Dict]:

        if not viewed_products:
            return []

        category_counts = Counter([p.category for p in viewed_products])
        preferred_categories = [cat for cat, _ in category_counts.most_common(3)]

        recommendations = []
        for category in preferred_categories:
            products = self._product_repo.get_by_category(category)

            for product in products:
                if product.id not in exclude_ids and len(recommendations) < limit:
                    recommendations.append({
                        **product.to_dict(),
                        'reason': f'Similar to {category} items you viewed'
                    })

        return recommendations

    def _get_collaborative_recommendations(
        self,
        viewed_product_ids: List[int],
        limit: int = 10
    ) -> List[Dict]:

        related_product_scores = defaultdict(int)

        for product_id in viewed_product_ids:
            related_ids = self._interaction_repo.get_related_products(product_id, limit=10)

            for idx, related_id in enumerate(related_ids):

                score = len(related_ids) - idx
                related_product_scores[related_id] += score

        sorted_product_ids = sorted(
            related_product_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        recommendations = []
        for product_id, score in sorted_product_ids:
            product = self._product_repo.get_by_id(product_id)
            if product:
                recommendations.append({
                    **product.to_dict(),
                    'reason': 'Users who viewed similar items also liked this',
                    'score': score
                })

        return recommendations

    def _get_popular_products(self, limit: int = 10) -> List[Dict]:

        popular = self._interaction_repo.get_popular_products(limit=limit)

        recommendations = []
        for item in popular:
            product = self._product_repo.get_by_id(item['product_id'])
            if product:
                recommendations.append({
                    **product.to_dict(),
                    'reason': 'Popular choice',
                    'interaction_count': item['count']
                })

        if len(recommendations) < limit:
            all_products = self._product_repo.get_all()

            sorted_products = sorted(
                all_products,
                key=lambda p: (p.rating or 0) * ((p.to_dict().get('reviews') or 0) + 1),
                reverse=True
            )

            existing_ids = {r['id'] for r in recommendations}
            for product in sorted_products:
                if product.id not in existing_ids and len(recommendations) < limit:
                    recommendations.append({
                        **product.to_dict(),
                        'reason': 'Highly rated'
                    })

        return recommendations

    def track_interaction(
        self,
        product_id: int,
        interaction_type: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> ProductInteraction:

        interaction = ProductInteraction(
            user_id=user_id,
            product_id=product_id,
            interaction_type=interaction_type,
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )

        return self._interaction_repo.create(interaction)

    def get_product_recommendations(self, product_id: int, limit: int = 6) -> List[Dict]:

        product = self._product_repo.get_by_id(product_id)
        if not product:
            return []

        recommendations = []

        category_products = self._product_repo.get_by_category(product.category)
        for p in category_products:
            if p.id != product_id and len(recommendations) < limit:
                recommendations.append({
                    **p.to_dict(),
                    'reason': f'More {product.category} items'
                })

        related_ids = self._interaction_repo.get_related_products(product_id, limit=limit)
        for related_id in related_ids:
            related_product = self._product_repo.get_by_id(related_id)
            if related_product and related_product.id not in [r['id'] for r in recommendations]:
                if len(recommendations) < limit:
                    recommendations.append({
                        **related_product.to_dict(),
                        'reason': 'Customers also viewed'
                    })

        return recommendations[:limit]
