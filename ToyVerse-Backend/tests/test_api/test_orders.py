import pytest

class TestOrdersAPI:
    def test_create_order_from_cart(self, client, customer_token, sample_product):
        client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 2},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        response = client.post(
            "/api/orders",
            json={
                "customer_details": {
                    "name": "Test Customer",
                    "email": "customer@test.com",
                    "phone": "1234567890",
                    "address": "123 Test St",
                    "city": "Test City",
                    "postal_code": "12345"
                },
                "payment_method": "COD"
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert "order_number" in data
        assert data["status"] == "pending"
        assert len(data["items"]) > 0

    def test_get_user_orders(self, client, customer_token, sample_product):
        client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 1},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        client.post(
            "/api/orders",
            json={
                "customer_details": {
                    "name": "Test",
                    "email": "test@test.com",
                    "phone": "123",
                    "address": "123",
                    "city": "City",
                    "postal_code": "123"
                },
                "payment_method": "COD"
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        response = client.get(
            "/api/orders",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_order_by_id(self, client, customer_token, sample_product):
        client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 1},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        create_response = client.post(
            "/api/orders",
            json={
                "customer_details": {
                    "name": "Test",
                    "email": "test@test.com",
                    "phone": "123",
                    "address": "123",
                    "city": "City",
                    "postal_code": "123"
                },
                "payment_method": "COD"
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        order_id = create_response.json()["id"]

        response = client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id

    def test_update_order_status_admin(self, client, admin_token, customer_token, sample_product):
        client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 1},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        create_response = client.post(
            "/api/orders",
            json={
                "customer_details": {
                    "name": "Test",
                    "email": "test@test.com",
                    "phone": "123",
                    "address": "123",
                    "city": "City",
                    "postal_code": "123"
                },
                "payment_method": "COD"
            },
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        order_id = create_response.json()["id"]

        response = client.put(
            f"/api/orders/{order_id}/status",
            json={"status": "processing"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
