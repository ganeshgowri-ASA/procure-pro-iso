"""
Pytest configuration and fixtures for TBE Scoring Engine tests.

Provides sample vendor data and bid information for comprehensive testing.
"""

from datetime import datetime
from uuid import uuid4, UUID

import pytest
from httpx import AsyncClient, ASGITransport

from src.models.vendor import Vendor, VendorStatus
from src.models.tbe import (
    VendorBid,
    DefaultCriteriaWeights,
    ISOStandard,
    TBEEvaluation,
    TBEEvaluationCreate,
)
from src.api.app import app


# ============================================================================
# Sample Vendor Data
# ============================================================================


@pytest.fixture
def sample_vendors() -> dict[UUID, Vendor]:
    """Create sample vendors for testing."""
    vendor_alpha = Vendor(
        id=uuid4(),
        name="Alpha Manufacturing Co.",
        code="ALPHA-001",
        email="sales@alphamfg.com",
        phone="+1-555-0101",
        address="123 Industrial Blvd, Chicago, IL 60601",
        country="USA",
        industry="Manufacturing",
        status=VendorStatus.ACTIVE,
        certifications=["ISO 9001:2015", "CE Mark", "UL Listed"],
        iso_standards=["ISO 9001", "ISO 14001"],
        quality_rating=92.5,
        delivery_rating=88.0,
        price_competitiveness=75.0,
    )

    vendor_beta = Vendor(
        id=uuid4(),
        name="Beta Tech Solutions",
        code="BETA-002",
        email="info@betatech.com",
        phone="+1-555-0102",
        address="456 Tech Park, San Jose, CA 95110",
        country="USA",
        industry="Technology",
        status=VendorStatus.ACTIVE,
        certifications=["ISO 9001:2015", "ISO 27001:2022", "SOC 2 Type II"],
        iso_standards=["ISO 9001", "ISO 27001", "ISO 17025"],
        quality_rating=95.0,
        delivery_rating=82.0,
        price_competitiveness=60.0,
    )

    vendor_gamma = Vendor(
        id=uuid4(),
        name="Gamma Industrial Ltd.",
        code="GAMMA-003",
        email="sales@gammaindustrial.com",
        phone="+44-20-7946-0103",
        address="789 Factory Lane, Birmingham, UK B1 1AA",
        country="UK",
        industry="Industrial Equipment",
        status=VendorStatus.ACTIVE,
        certifications=["ISO 9001:2015", "IATF 16949:2016", "CE Mark"],
        iso_standards=["ISO 9001", "IATF 16949", "ISO 45001"],
        quality_rating=88.0,
        delivery_rating=95.0,
        price_competitiveness=82.0,
    )

    vendor_delta = Vendor(
        id=uuid4(),
        name="Delta Precision Inc.",
        code="DELTA-004",
        email="orders@deltaprecision.com",
        phone="+1-555-0104",
        address="321 Precision Way, Detroit, MI 48201",
        country="USA",
        industry="Precision Manufacturing",
        status=VendorStatus.ACTIVE,
        certifications=["ISO 9001:2015", "AS 9100D", "NADCAP"],
        iso_standards=["ISO 9001", "AS 9100", "ISO 17025"],
        quality_rating=97.0,
        delivery_rating=78.0,
        price_competitiveness=55.0,
    )

    vendor_epsilon = Vendor(
        id=uuid4(),
        name="Epsilon Budget Supply",
        code="EPSILON-005",
        email="sales@epsilonbudget.com",
        phone="+1-555-0105",
        address="555 Economy Rd, Dallas, TX 75201",
        country="USA",
        industry="Supply Chain",
        status=VendorStatus.ACTIVE,
        certifications=["ISO 9001:2015"],
        iso_standards=["ISO 9001"],
        quality_rating=72.0,
        delivery_rating=85.0,
        price_competitiveness=95.0,
    )

    return {
        vendor_alpha.id: vendor_alpha,
        vendor_beta.id: vendor_beta,
        vendor_gamma.id: vendor_gamma,
        vendor_delta.id: vendor_delta,
        vendor_epsilon.id: vendor_epsilon,
    }


@pytest.fixture
def sample_bids(sample_vendors: dict[UUID, Vendor]) -> list[VendorBid]:
    """Create sample vendor bids for testing."""
    vendors = list(sample_vendors.values())

    bid_alpha = VendorBid(
        id=uuid4(),
        vendor_id=vendors[0].id,
        bid_reference="BID-ALPHA-2024-001",
        unit_price=15000.00,
        quantity=10,
        total_price=150000.00,
        currency="USD",
        shipping_cost=2500.00,
        installation_cost=5000.00,
        training_cost=3000.00,
        maintenance_cost_annual=4500.00,
        warranty_years=2,
        expected_lifespan_years=7,
        delivery_days=30,
        delivery_terms="FOB Destination",
        technical_specs={"power": "220V", "capacity": "1000 units/hr", "accuracy": "99.5%"},
        certifications=["ISO 9001:2015", "CE Mark", "UL Listed"],
        iso_compliance=["ISO 9001", "ISO 14001"],
        quality_score=92.5,
        past_performance_score=90.0,
    )

    bid_beta = VendorBid(
        id=uuid4(),
        vendor_id=vendors[1].id,
        bid_reference="BID-BETA-2024-001",
        unit_price=18500.00,
        quantity=10,
        total_price=185000.00,
        currency="USD",
        shipping_cost=1800.00,
        installation_cost=4500.00,
        training_cost=6000.00,
        maintenance_cost_annual=3500.00,
        warranty_years=3,
        expected_lifespan_years=8,
        delivery_days=45,
        delivery_terms="CIF",
        technical_specs={"power": "220V", "capacity": "1200 units/hr", "accuracy": "99.9%"},
        certifications=["ISO 9001:2015", "ISO 27001:2022", "SOC 2 Type II"],
        iso_compliance=["ISO 9001", "ISO 27001", "ISO 17025"],
        quality_score=95.0,
        past_performance_score=93.0,
    )

    bid_gamma = VendorBid(
        id=uuid4(),
        vendor_id=vendors[2].id,
        bid_reference="BID-GAMMA-2024-001",
        unit_price=14200.00,
        quantity=10,
        total_price=142000.00,
        currency="USD",
        shipping_cost=4000.00,
        installation_cost=3500.00,
        training_cost=2500.00,
        maintenance_cost_annual=5000.00,
        warranty_years=2,
        expected_lifespan_years=6,
        delivery_days=21,
        delivery_terms="DDP",
        technical_specs={"power": "220V", "capacity": "900 units/hr", "accuracy": "99.2%"},
        certifications=["ISO 9001:2015", "IATF 16949:2016", "CE Mark"],
        iso_compliance=["ISO 9001", "IATF 16949", "ISO 45001"],
        quality_score=88.0,
        past_performance_score=85.0,
    )

    bid_delta = VendorBid(
        id=uuid4(),
        vendor_id=vendors[3].id,
        bid_reference="BID-DELTA-2024-001",
        unit_price=22000.00,
        quantity=10,
        total_price=220000.00,
        currency="USD",
        shipping_cost=2000.00,
        installation_cost=8000.00,
        training_cost=5000.00,
        maintenance_cost_annual=3000.00,
        warranty_years=5,
        expected_lifespan_years=10,
        delivery_days=60,
        delivery_terms="FOB Origin",
        technical_specs={"power": "220V", "capacity": "1500 units/hr", "accuracy": "99.99%"},
        certifications=["ISO 9001:2015", "AS 9100D", "NADCAP"],
        iso_compliance=["ISO 9001", "AS 9100", "ISO 17025"],
        quality_score=97.0,
        past_performance_score=96.0,
    )

    bid_epsilon = VendorBid(
        id=uuid4(),
        vendor_id=vendors[4].id,
        bid_reference="BID-EPSILON-2024-001",
        unit_price=11500.00,
        quantity=10,
        total_price=115000.00,
        currency="USD",
        shipping_cost=1500.00,
        installation_cost=2000.00,
        training_cost=1000.00,
        maintenance_cost_annual=6000.00,
        warranty_years=1,
        expected_lifespan_years=5,
        delivery_days=28,
        delivery_terms="EXW",
        technical_specs={"power": "220V", "capacity": "800 units/hr", "accuracy": "98.5%"},
        certifications=["ISO 9001:2015"],
        iso_compliance=["ISO 9001"],
        quality_score=72.0,
        past_performance_score=70.0,
    )

    return [bid_alpha, bid_beta, bid_gamma, bid_delta, bid_epsilon]


@pytest.fixture
def default_weights() -> DefaultCriteriaWeights:
    """Create default criteria weights."""
    return DefaultCriteriaWeights(
        price=0.40,
        quality=0.25,
        delivery=0.20,
        compliance=0.15,
    )


@pytest.fixture
def balanced_weights() -> DefaultCriteriaWeights:
    """Create balanced criteria weights."""
    return DefaultCriteriaWeights(
        price=0.25,
        quality=0.25,
        delivery=0.25,
        compliance=0.25,
    )


@pytest.fixture
def required_iso_standards() -> list[ISOStandard]:
    """Create list of required ISO standards."""
    return [ISOStandard.ISO_9001, ISOStandard.ISO_17025]


@pytest.fixture
def required_certifications() -> list[str]:
    """Create list of required certifications."""
    return ["ISO 9001:2015", "CE Mark"]


@pytest.fixture
def sample_evaluation(
    default_weights: DefaultCriteriaWeights,
    required_iso_standards: list[ISOStandard],
    required_certifications: list[str],
) -> TBEEvaluation:
    """Create a sample TBE evaluation."""
    return TBEEvaluation(
        id=uuid4(),
        name="Test Equipment Procurement 2024",
        description="Evaluation of vendors for test equipment procurement",
        project_reference="PROJ-2024-001",
        criteria_weights=default_weights,
        required_iso_standards=required_iso_standards,
        required_certifications=required_certifications,
    )


# ============================================================================
# API Test Client
# ============================================================================


@pytest.fixture
async def async_client():
    """Create async test client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
