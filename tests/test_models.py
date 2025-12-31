"""Tests for RFQ data models."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError as PydanticValidationError

from procure_pro_iso.models.rfq import (
    Currency,
    DeliveryTerms,
    EquipmentItem,
    ParsedRFQResult,
    ParsingError,
    PriceBreakdown,
    QuoteStatus,
    RFQDocument,
    TechnicalSpecification,
    ValidationError,
    VendorQuote,
)


class TestCurrency:
    """Tests for Currency enum."""

    def test_currency_values(self):
        """Test that all expected currencies are available."""
        assert Currency.USD.value == "USD"
        assert Currency.EUR.value == "EUR"
        assert Currency.GBP.value == "GBP"
        assert Currency.JPY.value == "JPY"
        assert Currency.INR.value == "INR"
        assert Currency.CNY.value == "CNY"
        assert Currency.AED.value == "AED"
        assert Currency.OTHER.value == "OTHER"


class TestDeliveryTerms:
    """Tests for DeliveryTerms model."""

    def test_basic_delivery_terms(self):
        """Test creating basic delivery terms."""
        terms = DeliveryTerms(
            incoterm="FOB",
            delivery_time_days=30,
            delivery_location="New York",
        )
        assert terms.incoterm == "FOB"
        assert terms.delivery_time_days == 30
        assert terms.delivery_location == "New York"

    def test_incoterm_normalization(self):
        """Test that incoterm is normalized to uppercase."""
        terms = DeliveryTerms(incoterm="fob")
        assert terms.incoterm == "FOB"

        terms = DeliveryTerms(incoterm="  cif  ")
        assert terms.incoterm == "CIF"

    def test_optional_fields(self):
        """Test that optional fields default to None."""
        terms = DeliveryTerms()
        assert terms.incoterm is None
        assert terms.delivery_time_days is None
        assert terms.delivery_location is None
        assert terms.shipping_method is None
        assert terms.partial_shipment_allowed is None


class TestPriceBreakdown:
    """Tests for PriceBreakdown model."""

    def test_basic_pricing(self):
        """Test creating basic price breakdown."""
        price = PriceBreakdown(
            unit_price=Decimal("100.00"),
            quantity=5,
            currency=Currency.USD,
        )
        assert price.unit_price == Decimal("100.00")
        assert price.quantity == 5
        assert price.total_price == Decimal("500.00")

    def test_total_calculation(self):
        """Test that total is calculated automatically."""
        price = PriceBreakdown(
            unit_price=Decimal("250.50"),
            quantity=4,
        )
        assert price.total_price == Decimal("1002.00")

    def test_decimal_parsing_from_string(self):
        """Test parsing decimal values from strings."""
        price = PriceBreakdown(
            unit_price="$1,500.00",
            quantity=2,
        )
        assert price.unit_price == Decimal("1500.00")

    def test_decimal_parsing_from_float(self):
        """Test parsing decimal values from floats."""
        price = PriceBreakdown(
            unit_price=1500.00,
            quantity=1,
        )
        assert price.unit_price == Decimal("1500.0")

    def test_invalid_quantity(self):
        """Test that quantity must be positive."""
        with pytest.raises(PydanticValidationError):
            PriceBreakdown(unit_price=Decimal("100"), quantity=0)


class TestTechnicalSpecification:
    """Tests for TechnicalSpecification model."""

    def test_basic_spec(self):
        """Test creating basic technical specification."""
        spec = TechnicalSpecification(
            parameter="Wavelength Range",
            value="190-1100",
            unit="nm",
        )
        assert spec.parameter == "Wavelength Range"
        assert spec.value == "190-1100"
        assert spec.unit == "nm"

    def test_spec_without_unit(self):
        """Test specification without unit."""
        spec = TechnicalSpecification(
            parameter="Resolution",
            value="1920x1080",
        )
        assert spec.unit is None

    def test_spec_with_compliance(self):
        """Test specification with compliance flag."""
        spec = TechnicalSpecification(
            parameter="Temperature Range",
            value="0-100",
            unit="°C",
            is_compliant=True,
        )
        assert spec.is_compliant is True


class TestEquipmentItem:
    """Tests for EquipmentItem model."""

    def test_basic_item(self):
        """Test creating basic equipment item."""
        item = EquipmentItem(
            name="Spectrophotometer",
            model_number="SP-2000",
            manufacturer="TechLab",
            country_of_origin="Germany",
        )
        assert item.name == "Spectrophotometer"
        assert item.model_number == "SP-2000"
        assert item.manufacturer == "TechLab"
        assert item.country_of_origin == "Germany"

    def test_item_with_pricing(self):
        """Test item with pricing information."""
        pricing = PriceBreakdown(
            unit_price=Decimal("15000.00"),
            quantity=2,
            currency=Currency.EUR,
        )
        item = EquipmentItem(
            name="HPLC System",
            pricing=pricing,
        )
        assert item.pricing.unit_price == Decimal("15000.00")
        assert item.pricing.total_price == Decimal("30000.00")

    def test_item_with_specs(self):
        """Test item with technical specifications."""
        specs = [
            TechnicalSpecification(parameter="Pressure", value="600", unit="bar"),
            TechnicalSpecification(parameter="Flow Rate", value="0.001-10", unit="mL/min"),
        ]
        item = EquipmentItem(
            name="HPLC System",
            technical_specs=specs,
        )
        assert len(item.technical_specs) == 2

    def test_item_name_required(self):
        """Test that item name is required."""
        with pytest.raises(PydanticValidationError):
            EquipmentItem(name="")


class TestVendorQuote:
    """Tests for VendorQuote model."""

    def test_basic_quote(self):
        """Test creating basic vendor quote."""
        quote = VendorQuote(
            vendor_name="TechLab Solutions",
            quote_reference="TLS-Q-2024-001",
        )
        assert quote.vendor_name == "TechLab Solutions"
        assert quote.quote_reference == "TLS-Q-2024-001"
        assert quote.status == QuoteStatus.RECEIVED

    def test_quote_with_items(self):
        """Test quote with equipment items."""
        items = [
            EquipmentItem(
                name="Spectrophotometer",
                pricing=PriceBreakdown(unit_price=Decimal("15000"), quantity=2),
            ),
            EquipmentItem(
                name="pH Meter",
                pricing=PriceBreakdown(unit_price=Decimal("500"), quantity=3),
            ),
        ]
        quote = VendorQuote(
            vendor_name="TechLab",
            items=items,
        )
        assert len(quote.items) == 2

    def test_date_parsing(self):
        """Test parsing dates from various formats."""
        quote = VendorQuote(
            vendor_name="Test Vendor",
            quote_date="2024-12-15",
            validity_date="December 31, 2024",
        )
        assert quote.quote_date == date(2024, 12, 15)
        assert quote.validity_date == date(2024, 12, 31)

    def test_vendor_name_required(self):
        """Test that vendor name is required."""
        with pytest.raises(PydanticValidationError):
            VendorQuote(vendor_name="")


class TestRFQDocument:
    """Tests for RFQDocument model."""

    def test_basic_document(self):
        """Test creating basic RFQ document."""
        doc = RFQDocument(
            rfq_number="RFQ-2024-001",
            rfq_title="Laboratory Equipment Procurement",
        )
        assert doc.rfq_number == "RFQ-2024-001"
        assert doc.rfq_title == "Laboratory Equipment Procurement"
        assert doc.vendor_quotes == []

    def test_document_with_quotes(self):
        """Test document with vendor quotes."""
        quotes = [
            VendorQuote(vendor_name="Vendor A"),
            VendorQuote(vendor_name="Vendor B"),
            VendorQuote(vendor_name="Vendor C"),
        ]
        doc = RFQDocument(
            rfq_number="RFQ-2024-001",
            vendor_quotes=quotes,
        )
        assert len(doc.vendor_quotes) == 3


class TestParsedRFQResult:
    """Tests for ParsedRFQResult model."""

    def test_successful_result(self):
        """Test creating successful parsing result."""
        doc = RFQDocument(rfq_number="RFQ-001")
        result = ParsedRFQResult(
            success=True,
            document=doc,
            source_file="/path/to/file.xlsx",
            source_type="excel",
        )
        assert result.success is True
        assert result.document is not None
        assert result.parsing_errors == []

    def test_failed_result(self):
        """Test creating failed parsing result."""
        result = ParsedRFQResult(
            success=False,
            source_file="/path/to/file.xlsx",
            source_type="excel",
            parsing_errors=[
                ParsingError(error_type="FileNotFound", message="File not found"),
            ],
        )
        assert result.success is False
        assert len(result.parsing_errors) == 1

    def test_to_json(self):
        """Test JSON serialization."""
        doc = RFQDocument(rfq_number="RFQ-001")
        result = ParsedRFQResult(
            success=True,
            document=doc,
            source_file="test.xlsx",
            source_type="excel",
        )
        json_str = result.to_json()
        assert '"success": true' in json_str
        assert '"rfq_number": "RFQ-001"' in json_str

    def test_to_dict(self):
        """Test dictionary serialization."""
        doc = RFQDocument(rfq_number="RFQ-001")
        result = ParsedRFQResult(
            success=True,
            document=doc,
            source_file="test.xlsx",
            source_type="excel",
        )
        data = result.to_dict()
        assert data["success"] is True
        assert data["document"]["rfq_number"] == "RFQ-001"
