import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import Admin, Customer
from app.core.security import hash_password

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def admin_user(db_session):
    admin = Admin(
        username="testadmin",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role="admin",
        full_name="Test Admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def customer_user(db_session):
    customer = Customer(
        username="testcustomer",
        email="customer@test.com",
        password_hash=hash_password("customer123"),
        role="customer",
        full_name="Test Customer"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer

@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    response = client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "admin123"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def customer_token(client, customer_user):
    response = client.post(
        "/api/auth/login",
        json={"username": "testcustomer", "password": "customer123"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def sample_product(db_session):
    from app.models.product import Product
    product = Product(
        title="Test Toy",
        price=29.99,
        category="Sets",
        stock=10,
        rating=5,
        icon="🎮",
        description="A test toy",
        detailed_description="A detailed test toy description"
    )
    product.images = ["http://example.com/image1.jpg"]
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product
