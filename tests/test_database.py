"""Tests for database integration."""

import os
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from procure_pro_iso.database.models import (
    Base,
    DeliveryTermsDB,
    EquipmentItemDB,
    ParseResultDB,
    PriceBreakdownDB,
    RFQDocumentDB,
    TechnicalSpecDB,
    VendorQuoteDB,
)
from procure_pro_iso.database.repository import RFQRepository
from procure_pro_iso.models.rfq import (
    Currency,
    DeliveryTerms,
    EquipmentItem,
    ParsedRFQResult,
    PriceBreakdown,
    RFQDocument,
    TechnicalSpecification,
    VendorQuote,
)


# Use SQLite for testing (in-memory)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def repository(test_session):
    """Create a repository instance for testing."""
    return RFQRepository(test_session)


@pytest.fixture
def sample_rfq_document():
    """Create a sample RFQ document for testing."""
    return RFQDocument(
        rfq_number="RFQ-2024-001",
        rfq_title="Laboratory Equipment Procurement",
        project_name="Lab Upgrade Project",
        vendor_quotes=[
            VendorQuote(
                vendor_name="TechLab Solutions",
                quote_reference="TLS-Q-2024-001",
                items=[
                    EquipmentItem(
                        name="Spectrophotometer UV-VIS",
                        model_number="SP-2000",
                        manufacturer="TechLab",
                        country_of_origin="Germany",
                        pricing=PriceBreakdown(
                            unit_price=Decimal("15000.00"),
                            quantity=2,
                            currency=Currency.USD,
                        ),
                        technical_specs=[
                            TechnicalSpecification(
                                parameter="Wavelength Range",
                                value="190-1100",
                                unit="nm",
                            ),
                        ],
                        delivery=DeliveryTerms(
                            delivery_time_days=45,
                            incoterm="FOB",
                        ),
                    ),
                    EquipmentItem(
                        name="Digital Balance",
                        model_number="DB-500",
                        pricing=PriceBreakdown(
                            unit_price=Decimal("2500.00"),
                            quantity=5,
                        ),
                    ),
                ],
            ),
            VendorQuote(
                vendor_name="ChemAnalytics Inc",
                items=[
                    EquipmentItem(
                        name="HPLC System",
                        model_number="HPLC-3500",
                        pricing=PriceBreakdown(
                            unit_price=Decimal("85000.00"),
                            quantity=1,
                        ),
                    ),
                ],
            ),
        ],
    )


class TestRFQDocumentDB:
    """Tests for RFQ document database model."""

    def test_create_rfq_document(self, test_session):
        """Test creating an RFQ document."""
        rfq = RFQDocumentDB(
            rfq_number="RFQ-2024-001",
            rfq_title="Test RFQ",
            project_name="Test Project",
            status="active",
        )
        test_session.add(rfq)
        test_session.commit()

        assert rfq.id is not None
        assert rfq.rfq_number == "RFQ-2024-001"
        assert rfq.created_at is not None

    def test_rfq_with_vendor_quotes(self, test_session):
        """Test RFQ with vendor quotes relationship."""
        rfq = RFQDocumentDB(
            rfq_number="RFQ-2024-002",
            rfq_title="Test RFQ with Quotes",
        )
        test_session.add(rfq)
        test_session.flush()

        quote = VendorQuoteDB(
            rfq_document_id=rfq.id,
            vendor_name="Test Vendor",
            status="received",
        )
        test_session.add(quote)
        test_session.commit()

        assert len(rfq.vendor_quotes) == 1
        assert rfq.vendor_quotes[0].vendor_name == "Test Vendor"


class TestVendorQuoteDB:
    """Tests for vendor quote database model."""

    def test_create_vendor_quote(self, test_session):
        """Test creating a vendor quote."""
        # First create an RFQ
        rfq = RFQDocumentDB(rfq_number="RFQ-001")
        test_session.add(rfq)
        test_session.flush()

        quote = VendorQuoteDB(
            rfq_document_id=rfq.id,
            vendor_name="TechLab Solutions",
            vendor_code="TLS",
            total_amount=Decimal("50000.00"),
            currency="USD",
        )
        test_session.add(quote)
        test_session.commit()

        assert quote.id is not None
        assert quote.total_amount == Decimal("50000.00")

    def test_vendor_quote_with_items(self, test_session):
        """Test vendor quote with equipment items."""
        rfq = RFQDocumentDB(rfq_number="RFQ-002")
        test_session.add(rfq)
        test_session.flush()

        quote = VendorQuoteDB(
            rfq_document_id=rfq.id,
            vendor_name="Test Vendor",
        )
        test_session.add(quote)
        test_session.flush()

        item = EquipmentItemDB(
            vendor_quote_id=quote.id,
            name="Test Equipment",
            model_number="TE-100",
        )
        test_session.add(item)
        test_session.commit()

        assert len(quote.items) == 1
        assert quote.items[0].name == "Test Equipment"


class TestEquipmentItemDB:
    """Tests for equipment item database model."""

    def test_create_equipment_item(self, test_session):
        """Test creating an equipment item."""
        rfq = RFQDocumentDB(rfq_number="RFQ-003")
        test_session.add(rfq)
        test_session.flush()

        quote = VendorQuoteDB(rfq_document_id=rfq.id, vendor_name="Vendor")
        test_session.add(quote)
        test_session.flush()

        item = EquipmentItemDB(
            vendor_quote_id=quote.id,
            name="Spectrophotometer",
            model_number="SP-2000",
            manufacturer="TechLab",
            country_of_origin="Germany",
        )
        test_session.add(item)
        test_session.commit()

        assert item.id is not None
        assert item.name == "Spectrophotometer"

    def test_item_with_pricing(self, test_session):
        """Test equipment item with pricing."""
        rfq = RFQDocumentDB(rfq_number="RFQ-004")
        test_session.add(rfq)
        test_session.flush()

        quote = VendorQuoteDB(rfq_document_id=rfq.id, vendor_name="Vendor")
        test_session.add(quote)
        test_session.flush()

        item = EquipmentItemDB(vendor_quote_id=quote.id, name="Item")
        test_session.add(item)
        test_session.flush()

        pricing = PriceBreakdownDB(
            equipment_item_id=item.id,
            unit_price=Decimal("1000.00"),
            quantity=5,
            total_price=Decimal("5000.00"),
        )
        test_session.add(pricing)
        test_session.commit()

        assert item.pricing is not None
        assert item.pricing.unit_price == Decimal("1000.00")


class TestRFQRepository:
    """Tests for RFQ repository."""

    def test_save_rfq_document(self, repository, sample_rfq_document):
        """Test saving an RFQ document."""
        rfq_db = repository.save_rfq_document(sample_rfq_document)

        assert rfq_db.id is not None
        assert rfq_db.rfq_number == "RFQ-2024-001"
        assert len(rfq_db.vendor_quotes) == 2

    def test_get_by_id(self, repository, sample_rfq_document):
        """Test retrieving RFQ by ID."""
        rfq_db = repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        retrieved = repository.get_by_id(rfq_db.id)

        assert retrieved is not None
        assert retrieved.rfq_number == "RFQ-2024-001"

    def test_get_by_rfq_number(self, repository, sample_rfq_document):
        """Test retrieving RFQ by number."""
        repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        retrieved = repository.get_by_rfq_number("RFQ-2024-001")

        assert retrieved is not None
        assert retrieved.rfq_title == "Laboratory Equipment Procurement"

    def test_get_with_quotes(self, repository, sample_rfq_document):
        """Test retrieving RFQ with vendor quotes loaded."""
        rfq_db = repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        retrieved = repository.get_with_quotes(rfq_db.id)

        assert retrieved is not None
        assert len(retrieved.vendor_quotes) == 2

    def test_list_all(self, repository, sample_rfq_document):
        """Test listing all RFQ documents."""
        repository.save_rfq_document(sample_rfq_document)

        # Create another RFQ
        rfq2 = RFQDocument(
            rfq_number="RFQ-2024-002",
            rfq_title="Another RFQ",
        )
        repository.save_rfq_document(rfq2)
        repository.session.commit()

        rfqs = repository.list_all()

        assert len(rfqs) == 2

    def test_search(self, repository, sample_rfq_document):
        """Test searching RFQ documents."""
        repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        results = repository.search("Laboratory")

        assert len(results) == 1
        assert results[0].rfq_title == "Laboratory Equipment Procurement"

    def test_get_vendor_quotes(self, repository, sample_rfq_document):
        """Test getting vendor quotes for an RFQ."""
        rfq_db = repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        quotes = repository.get_vendor_quotes(rfq_db.id)

        assert len(quotes) == 2
        vendor_names = {q.vendor_name for q in quotes}
        assert "TechLab Solutions" in vendor_names
        assert "ChemAnalytics Inc" in vendor_names

    def test_get_statistics(self, repository, sample_rfq_document):
        """Test getting database statistics."""
        repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        stats = repository.get_statistics()

        assert stats["total_rfqs"] == 1
        assert stats["total_vendors"] == 2
        assert stats["total_items"] == 3

    def test_delete_rfq(self, repository, sample_rfq_document):
        """Test deleting an RFQ document."""
        rfq_db = repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        result = repository.delete(rfq_db.id)

        assert result is True
        assert repository.get_by_id(rfq_db.id) is None

    def test_to_pydantic(self, repository, sample_rfq_document):
        """Test converting database model to Pydantic model."""
        rfq_db = repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        rfq_db = repository.get_with_quotes(rfq_db.id)
        pydantic_doc = repository.to_pydantic(rfq_db)

        assert isinstance(pydantic_doc, RFQDocument)
        assert pydantic_doc.rfq_number == "RFQ-2024-001"
        assert len(pydantic_doc.vendor_quotes) == 2

    def test_save_parsed_result(self, repository, sample_rfq_document):
        """Test saving a parsed result."""
        result = ParsedRFQResult(
            success=True,
            document=sample_rfq_document,
            source_file="/path/to/test.xlsx",
            source_type="excel",
        )

        parse_db = repository.save_parsed_result(result, processing_time_ms=150)

        assert parse_db.id is not None
        assert parse_db.success is True
        assert parse_db.processing_time_ms == 150
        assert parse_db.rfq_document_id is not None


class TestCascadeDelete:
    """Tests for cascade delete behavior."""

    def test_delete_rfq_cascades_to_quotes(self, repository, sample_rfq_document):
        """Test that deleting RFQ cascades to vendor quotes."""
        rfq_db = repository.save_rfq_document(sample_rfq_document)
        rfq_id = rfq_db.id
        repository.session.commit()

        # Get quote IDs before delete
        quotes = repository.get_vendor_quotes(rfq_id)
        quote_ids = [q.id for q in quotes]

        # Delete RFQ
        repository.delete(rfq_id)
        repository.session.commit()

        # Verify quotes are deleted
        for quote_id in quote_ids:
            assert repository.session.get(VendorQuoteDB, quote_id) is None

    def test_delete_vendor_quote(self, repository, sample_rfq_document):
        """Test deleting a single vendor quote."""
        rfq_db = repository.save_rfq_document(sample_rfq_document)
        repository.session.commit()

        quotes = repository.get_vendor_quotes(rfq_db.id)
        quote_to_delete = quotes[0]

        result = repository.delete_vendor_quote(quote_to_delete.id)

        assert result is True

        # Verify only one quote remains
        remaining_quotes = repository.get_vendor_quotes(rfq_db.id)
        assert len(remaining_quotes) == 1
