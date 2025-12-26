import pytest

class TestProductsAPI:
    def test_get_all_products(self, client, sample_product):
        response = client.get("/api/products")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_product_by_id(self, client, sample_product):
        response = client.get(f"/api/products/{sample_product.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_product.id
        assert data["title"] == sample_product.title

    def test_get_nonexistent_product(self, client):
        response = client.get("/api/products/99999")
        assert response.status_code == 404

    def test_create_product_admin(self, client, admin_token):
        response = client.post(
            "/api/products",
            json={
                "title": "New Product",
                "price": 59.99,
                "category": "Plushies",
                "stock": 15,
                "rating": 4,
                "icon": "🧸",
                "description": "A new plushie",
                "images": ["http://example.com/image.jpg"]
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Product"
        assert data["category"] == "Plushies"

    def test_create_product_customer_forbidden(self, client, customer_token):
        response = client.post(
            "/api/products",
            json={
                "title": "New Product",
                "price": 59.99,
                "category": "Plushies",
                "stock": 15
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 403

    def test_update_product_admin(self, client, admin_token, sample_product):
        response = client.put(
            f"/api/products/{sample_product.id}",
            json={"stock": 100},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock"] == 100

    def test_delete_product_admin(self, client, admin_token, sample_product):
        response = client.delete(
            f"/api/products/{sample_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204

    def test_filter_products_by_category(self, client, sample_product):
        response = client.get("/api/products?category=Sets")

        assert response.status_code == 200
        data = response.json()
        assert all(p["category"] == "Sets" for p in data)
