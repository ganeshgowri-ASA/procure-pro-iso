"""Test configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.database import Base, get_db
from app.main import app

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ==================== Test Data Factories ====================


@pytest.fixture
def vendor_data():
    """Sample vendor data for testing."""
    return {
        "code": "VND001",
        "name": "Test Vendor Inc.",
        "legal_name": "Test Vendor Incorporated",
        "email": "contact@testvendor.com",
        "phone": "+1-555-0100",
        "address_line1": "123 Test Street",
        "city": "Test City",
        "state": "Test State",
        "postal_code": "12345",
        "country": "USA",
        "status": "pending",
    }


@pytest.fixture
def category_data():
    """Sample category data for testing."""
    return {
        "name": "Electronics",
        "description": "Electronic components and equipment",
    }


@pytest.fixture
def certification_data():
    """Sample certification data for testing."""
    return {
        "certification_type": "ISO 9001",
        "certification_number": "CERT-001",
        "issuing_body": "ISO Certification Authority",
    }


@pytest.fixture
def contact_data():
    """Sample contact data for testing."""
    return {
        "name": "John Doe",
        "title": "Sales Manager",
        "email": "john.doe@testvendor.com",
        "phone": "+1-555-0101",
        "is_primary": True,
    }


@pytest.fixture
def rating_data():
    """Sample rating data for testing."""
    return {
        "rating_period": "2024-Q1",
        "quality_rating": 4.5,
        "delivery_rating": 4.0,
        "price_rating": 3.5,
        "service_rating": 4.5,
        "communication_rating": 4.0,
        "orders_placed": 10,
        "orders_completed": 10,
        "orders_on_time": 9,
        "defect_count": 1,
        "total_value": 50000.0,
        "evaluated_by": "Procurement Team",
    }


@pytest.fixture
def rfq_data():
    """Sample RFQ data for testing."""
    return {
        "title": "Office Equipment Procurement",
        "description": "Procurement of office equipment for new building",
        "priority": "normal",
        "currency": "USD",
        "validity_period_days": 30,
        "delivery_terms": "FOB Destination",
        "payment_terms": "Net 30",
        "items": [],
        "vendor_ids": [],
    }


@pytest.fixture
def rfq_item_data():
    """Sample RFQ item data for testing."""
    return {
        "item_number": 1,
        "name": "Desktop Computer",
        "description": "High-performance desktop computer",
        "quantity": 10,
        "unit": "pcs",
        "specifications": "Intel i7, 16GB RAM, 512GB SSD",
        "brand_preference": "Dell",
        "is_mandatory": True,
        "estimated_unit_price": 1000.0,
    }


@pytest.fixture
def quotation_item_data():
    """Sample quotation item data for testing."""
    return {
        "unit_price": 950.0,
        "quantity": 10,
        "offered_brand": "Dell",
        "offered_model": "OptiPlex 7080",
        "lead_time_days": 14,
        "availability": "In Stock",
    }
