import pytest
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository

class TestProductService:
    def test_create_product(self, db_session):
        repo = ProductRepository(db_session)
        service = ProductService(repo)

        product_data = {
            'title': 'New Toy',
            'price': 49.99,
            'category': 'Blocks',
            'stock': 20,
            'rating': 4,
            'icon': '🧱',
            'description': 'A new toy',
            'images': ['http://example.com/image.jpg']
        }

        product = service.create(product_data)

        assert product is not None
        assert product.title == 'New Toy'
        assert float(product.price) == 49.99
        assert product.category == 'Blocks'
        assert product.stock == 20

    def test_get_product_by_id(self, db_session, sample_product):
        repo = ProductRepository(db_session)
        service = ProductService(repo)

        product = service.get_by_id(sample_product.id)

        assert product is not None
        assert product.id == sample_product.id
        assert product.title == sample_product.title

    def test_update_product(self, db_session, sample_product):
        repo = ProductRepository(db_session)
        service = ProductService(repo)

        update_data = {'stock': 50, 'price': 39.99}
        updated_product = service.update(sample_product.id, update_data)

        assert updated_product is not None
        assert updated_product.stock == 50
        assert float(updated_product.price) == 39.99

    def test_delete_product(self, db_session, sample_product):
        repo = ProductRepository(db_session)
        service = ProductService(repo)

        result = service.delete(sample_product.id)
        assert result is True

        deleted_product = service.get_by_id(sample_product.id)
        assert deleted_product is None

    def test_filter_products_by_category(self, db_session, sample_product):
        repo = ProductRepository(db_session)
        service = ProductService(repo)

        products = service.get_by_category("Sets")

        assert len(products) > 0
        assert all(p.category == "Sets" for p in products)

    def test_update_stock(self, db_session, sample_product):
        repo = ProductRepository(db_session)
        service = ProductService(repo)

        updated = service.update_stock(sample_product.id, 5)

        assert updated is not None
        assert updated.stock == 15

    def test_update_stock_insufficient(self, db_session, sample_product):
        repo = ProductRepository(db_session)
        service = ProductService(repo)

        updated = service.update_stock(sample_product.id, -20)
        assert updated is None
