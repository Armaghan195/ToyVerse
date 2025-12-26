import pytest

class TestCartAPI:
    def test_get_empty_cart(self, client, customer_token):
        response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["item_count"] == 0

    def test_add_to_cart(self, client, customer_token, sample_product):
        response = client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 2},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == sample_product.id
        assert data["quantity"] == 2

    def test_add_to_cart_insufficient_stock(self, client, customer_token, sample_product):
        response = client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 100},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert response.status_code == 400

    def test_update_cart_item(self, client, customer_token, sample_product):
        add_response = client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 2},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        cart_item_id = add_response.json()["id"]

        update_response = client.put(
            f"/api/cart/{cart_item_id}",
            json={"quantity": 5},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["quantity"] == 5

    def test_remove_from_cart(self, client, customer_token, sample_product):
        add_response = client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 2},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        cart_item_id = add_response.json()["id"]

        delete_response = client.delete(
            f"/api/cart/{cart_item_id}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert delete_response.status_code == 204

    def test_clear_cart(self, client, customer_token, sample_product):
        client.post(
            "/api/cart/add",
            json={"product_id": sample_product.id, "quantity": 2},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        clear_response = client.delete(
            "/api/cart/clear",
            headers={"Authorization": f"Bearer {customer_token}"}
        )

        assert clear_response.status_code == 204

        cart_response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert cart_response.json()["item_count"] == 0
