import pytest
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.core.security import verify_password

class TestAuthService:
    def test_register_user(self, db_session):
        repo = UserRepository(db_session)
        service = AuthService(repo)

        user_data = UserCreate(
            username="newuser",
            email="newuser@test.com",
            password="password123",
            role="customer"
        )

        user = service.register(user_data)

        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@test.com"
        assert user.role == "customer"
        assert verify_password("password123", user.password_hash)

    def test_register_duplicate_username(self, db_session, customer_user):
        repo = UserRepository(db_session)
        service = AuthService(repo)

        user_data = UserCreate(
            username="testcustomer",
            email="different@test.com",
            password="password123",
            role="customer"
        )

        user = service.register(user_data)
        assert user is None

    def test_authenticate_valid_credentials(self, db_session, customer_user):
        repo = UserRepository(db_session)
        service = AuthService(repo)

        user = service.authenticate("testcustomer", "customer123")

        assert user is not None
        assert user.username == "testcustomer"

    def test_authenticate_invalid_password(self, db_session, customer_user):
        repo = UserRepository(db_session)
        service = AuthService(repo)

        user = service.authenticate("testcustomer", "wrongpassword")
        assert user is None

    def test_create_token(self, db_session, customer_user):
        repo = UserRepository(db_session)
        service = AuthService(repo)

        token = service.create_token(customer_user)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_get_user_by_token(self, db_session, customer_user):
        repo = UserRepository(db_session)
        service = AuthService(repo)

        token = service.create_token(customer_user)
        retrieved_user = service.get_user_by_token(token)

        assert retrieved_user is not None
        assert retrieved_user.id == customer_user.id
        assert retrieved_user.username == customer_user.username
