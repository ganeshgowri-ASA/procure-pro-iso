"""Tests for RFQ service layer."""

from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from procure_pro_iso.database.connection import DatabaseManager
from procure_pro_iso.database.models import Base
from procure_pro_iso.models.rfq import (
    Currency,
    EquipmentItem,
    ParsedRFQResult,
    PriceBreakdown,
    RFQDocument,
    VendorQuote,
)
from procure_pro_iso.parsers.rfq_parser import RFQParser
from procure_pro_iso.services.rfq_service import RFQService


# Use SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


class MockDatabaseManager:
    """Mock database manager for testing."""

    def __init__(self, url: str = TEST_DATABASE_URL):
        self.engine = create_engine(url, echo=False)
        Base.metadata.create_all(self.engine)
        self._session_factory = sessionmaker(bind=self.engine)

    def session_scope(self):
        """Provide a transactional scope."""
        from contextlib import contextmanager

        @contextmanager
        def _scope():
            session = self._session_factory()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

        return _scope()

    def dispose(self):
        """Dispose of the engine."""
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager for testing."""
    manager = MockDatabaseManager()
    yield manager
    manager.dispose()


@pytest.fixture
def rfq_service(mock_db_manager):
    """Create an RFQ service instance for testing."""
    return RFQService(db_manager=mock_db_manager)


@pytest.fixture
def sample_parsed_result():
    """Create a sample parsed result for testing."""
    return ParsedRFQResult(
        success=True,
        document=RFQDocument(
            rfq_number="RFQ-TEST-001",
            rfq_title="Test RFQ",
            vendor_quotes=[
                VendorQuote(
                    vendor_name="Test Vendor",
                    items=[
                        EquipmentItem(
                            name="Test Equipment",
                            model_number="TE-100",
                            pricing=PriceBreakdown(
                                unit_price=Decimal("1000.00"),
                                quantity=2,
                            ),
                        ),
                    ],
                ),
            ],
        ),
        source_file="/test/file.xlsx",
        source_type="excel",
    )


class TestRFQService:
    """Tests for RFQService class."""

    def test_service_initialization(self, mock_db_manager):
        """Test service initialization."""
        service = RFQService(db_manager=mock_db_manager)
        assert service.db_manager is not None
        assert service.parser is not None

    def test_parse_and_save_csv(self, rfq_service, sample_csv_path):
        """Test parsing and saving a CSV file."""
        result = rfq_service.parse_and_save(sample_csv_path)

        assert result["success"] is True
        assert result["parse_result_id"] is not None
        assert result["source_type"] == "csv"
        assert "processing_time_ms" in result

    def test_parse_and_save_summary(self, rfq_service, sample_csv_path):
        """Test that parse_and_save includes summary."""
        result = rfq_service.parse_and_save(sample_csv_path)

        assert "summary" in result
        assert "vendor_count" in result["summary"]
        assert "total_items" in result["summary"]

    def test_parse_and_save_nonexistent_file(self, rfq_service):
        """Test parsing a non-existent file."""
        result = rfq_service.parse_and_save("/nonexistent/file.xlsx")

        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_get_rfq(self, rfq_service, sample_csv_path):
        """Test retrieving an RFQ by ID."""
        # First parse and save
        parse_result = rfq_service.parse_and_save(sample_csv_path)
        rfq_id = parse_result["rfq_document_id"]

        if rfq_id:
            rfq = rfq_service.get_rfq(rfq_id)
            assert rfq is not None
            assert isinstance(rfq, RFQDocument)

    def test_list_rfqs(self, rfq_service, sample_csv_path, multi_vendor_csv_path):
        """Test listing RFQ documents."""
        # Parse and save multiple files
        rfq_service.parse_and_save(sample_csv_path)
        rfq_service.parse_and_save(multi_vendor_csv_path)

        rfqs = rfq_service.list_rfqs()

        assert len(rfqs) >= 1
        assert all("id" in rfq for rfq in rfqs)
        assert all("vendor_count" in rfq for rfq in rfqs)

    def test_list_rfqs_pagination(self, rfq_service, sample_csv_path):
        """Test listing with pagination."""
        rfq_service.parse_and_save(sample_csv_path)

        rfqs = rfq_service.list_rfqs(skip=0, limit=10)

        assert isinstance(rfqs, list)

    def test_get_vendor_quotes(self, rfq_service, sample_csv_path):
        """Test getting vendor quotes for an RFQ."""
        parse_result = rfq_service.parse_and_save(sample_csv_path)
        rfq_id = parse_result.get("rfq_document_id")

        if rfq_id:
            quotes = rfq_service.get_vendor_quotes(rfq_id)

            assert isinstance(quotes, list)
            for quote in quotes:
                assert "vendor_name" in quote
                assert "item_count" in quote

    def test_compare_vendors(self, rfq_service, multi_vendor_csv_path):
        """Test vendor comparison."""
        parse_result = rfq_service.parse_and_save(multi_vendor_csv_path)
        rfq_id = parse_result.get("rfq_document_id")

        if rfq_id:
            comparison = rfq_service.compare_vendors(rfq_id)

            assert "vendor_count" in comparison
            assert "vendors" in comparison
            assert isinstance(comparison["vendors"], list)

    def test_get_statistics(self, rfq_service, sample_csv_path):
        """Test getting database statistics."""
        rfq_service.parse_and_save(sample_csv_path)

        stats = rfq_service.get_statistics()

        assert "total_rfqs" in stats
        assert "total_vendors" in stats
        assert "total_items" in stats

    def test_delete_rfq(self, rfq_service, sample_csv_path):
        """Test deleting an RFQ."""
        parse_result = rfq_service.parse_and_save(sample_csv_path)
        rfq_id = parse_result.get("rfq_document_id")

        if rfq_id:
            result = rfq_service.delete_rfq(rfq_id)
            assert result is True

            # Verify it's deleted
            rfq = rfq_service.get_rfq(rfq_id)
            assert rfq is None

    def test_export_to_json(self, rfq_service, sample_csv_path):
        """Test exporting RFQ to JSON."""
        parse_result = rfq_service.parse_and_save(sample_csv_path)
        rfq_id = parse_result.get("rfq_document_id")

        if rfq_id:
            json_str = rfq_service.export_to_json(rfq_id)

            assert json_str is not None
            assert isinstance(json_str, str)
            assert "success" in json_str

    def test_parse_multiple_and_save(
        self, rfq_service, sample_csv_path, multi_vendor_csv_path
    ):
        """Test parsing and saving multiple files."""
        result = rfq_service.parse_multiple_and_save(
            [sample_csv_path, multi_vendor_csv_path]
        )

        assert result["total_files"] == 2
        assert result["successful"] >= 0
        assert len(result["results"]) == 2


class TestRFQServiceEdgeCases:
    """Tests for edge cases in RFQ service."""

    def test_get_nonexistent_rfq(self, rfq_service):
        """Test getting a non-existent RFQ."""
        from uuid import uuid4

        rfq = rfq_service.get_rfq(uuid4())
        assert rfq is None

    def test_delete_nonexistent_rfq(self, rfq_service):
        """Test deleting a non-existent RFQ."""
        from uuid import uuid4

        result = rfq_service.delete_rfq(uuid4())
        assert result is False

    def test_export_nonexistent_rfq(self, rfq_service):
        """Test exporting a non-existent RFQ."""
        from uuid import uuid4

        json_str = rfq_service.export_to_json(uuid4())
        assert json_str is None

    def test_get_vendor_quotes_nonexistent(self, rfq_service):
        """Test getting vendor quotes for non-existent RFQ."""
        from uuid import uuid4

        quotes = rfq_service.get_vendor_quotes(uuid4())
        assert quotes == []

    def test_search_rfqs_empty_results(self, rfq_service):
        """Test searching with no matches."""
        results = rfq_service.search_rfqs("nonexistent_query_12345")
        assert results == []
