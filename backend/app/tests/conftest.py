"""
Pytest configuration and fixtures for testing.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.db.models.user import User, UserRole


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create a test client with database."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def test_user(db) -> User:
    """Create a test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role=UserRole.REGULAR,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db) -> User:
    """Create a test admin user."""
    admin = User(
        name="Test Admin",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def test_reviewer(db) -> User:
    """Create a test reviewer user."""
    reviewer = User(
        name="Test Reviewer",
        email="reviewer@example.com",
        password_hash=get_password_hash("reviewerpassword123"),
        role=UserRole.REVIEWER,
        is_active=True
    )
    db.add(reviewer)
    db.commit()
    db.refresh(reviewer)
    return reviewer


@pytest.fixture(scope="function")
def user_token(test_user) -> str:
    """Create access token for test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture(scope="function")
def admin_token(test_admin) -> str:
    """Create access token for test admin."""
    return create_access_token(data={"sub": str(test_admin.id)})


@pytest.fixture(scope="function")
def reviewer_token(test_reviewer) -> str:
    """Create access token for test reviewer."""
    return create_access_token(data={"sub": str(test_reviewer.id)})


@pytest.fixture(scope="function")
def auth_headers(user_token) -> dict:
    """Create authorization headers for test user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="function")
def admin_headers(admin_token) -> dict:
    """Create authorization headers for admin."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def reviewer_headers(reviewer_token) -> dict:
    """Create authorization headers for reviewer."""
    return {"Authorization": f"Bearer {reviewer_token}"}
