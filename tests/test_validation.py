"""Tests for data validation in RFQ parser."""

from decimal import Decimal
from pathlib import Path

import pytest

from procure_pro_iso.models.rfq import (
    Currency,
    DeliveryTerms,
    EquipmentItem,
    PriceBreakdown,
    TechnicalSpecification,
    VendorQuote,
)
from procure_pro_iso.parsers.base import BaseParser


class TestPriceValidation:
    """Tests for price validation and parsing."""

    def test_valid_price_formats(self):
        """Test various valid price formats."""
        test_cases = [
            (Decimal("100.00"), 1, Currency.USD),
            (Decimal("1500.50"), 2, Currency.EUR),
            (Decimal("50000"), 1, Currency.GBP),
        ]

        for unit_price, qty, currency in test_cases:
            price = PriceBreakdown(
                unit_price=unit_price,
                quantity=qty,
                currency=currency,
            )
            assert price.total_price == unit_price * qty

    def test_price_from_string(self):
        """Test price parsing from string values."""
        price = PriceBreakdown(
            unit_price="$1,500.00",
            quantity=2,
        )
        assert price.unit_price == Decimal("1500.00")
        assert price.total_price == Decimal("3000.00")

    def test_price_from_float(self):
        """Test price parsing from float values."""
        price = PriceBreakdown(
            unit_price=1500.00,
            quantity=1,
        )
        assert price.unit_price == Decimal("1500.0")

    def test_price_with_all_components(self):
        """Test price with all cost components."""
        price = PriceBreakdown(
            unit_price=Decimal("1000.00"),
            quantity=2,
            shipping_cost=Decimal("150.00"),
            installation_cost=Decimal("500.00"),
            warranty_cost=Decimal("100.00"),
            tax_percent=Decimal("10"),
        )
        assert price.total_price == Decimal("2000.00")


class TestDeliveryValidation:
    """Tests for delivery terms validation."""

    def test_valid_incoterms(self):
        """Test all valid incoterms."""
        valid_incoterms = [
            "EXW", "FCA", "CPT", "CIP", "DAP", "DPU", "DDP",
            "FAS", "FOB", "CFR", "CIF"
        ]

        for incoterm in valid_incoterms:
            terms = DeliveryTerms(incoterm=incoterm)
            assert terms.incoterm == incoterm.upper()

    def test_incoterm_case_normalization(self):
        """Test that incoterms are normalized to uppercase."""
        terms = DeliveryTerms(incoterm="fob")
        assert terms.incoterm == "FOB"

        terms = DeliveryTerms(incoterm="Cif")
        assert terms.incoterm == "CIF"

    def test_delivery_time_validation(self):
        """Test delivery time validation."""
        terms = DeliveryTerms(delivery_time_days=30)
        assert terms.delivery_time_days == 30

        # Zero should be valid
        terms = DeliveryTerms(delivery_time_days=0)
        assert terms.delivery_time_days == 0


class TestTechnicalSpecValidation:
    """Tests for technical specification validation."""

    def test_valid_spec(self):
        """Test valid technical specification."""
        spec = TechnicalSpecification(
            parameter="Wavelength Range",
            value="190-1100",
            unit="nm",
            is_compliant=True,
        )
        assert spec.parameter == "Wavelength Range"
        assert spec.value == "190-1100"
        assert spec.unit == "nm"
        assert spec.is_compliant is True

    def test_spec_without_optional_fields(self):
        """Test spec with only required fields."""
        spec = TechnicalSpecification(
            parameter="Resolution",
            value="1920x1080",
        )
        assert spec.parameter == "Resolution"
        assert spec.value == "1920x1080"
        assert spec.unit is None
        assert spec.is_compliant is None


class TestEquipmentItemValidation:
    """Tests for equipment item validation."""

    def test_valid_item(self):
        """Test valid equipment item."""
        item = EquipmentItem(
            name="Spectrophotometer UV-VIS",
            model_number="SP-2000",
            manufacturer="TechLab",
            country_of_origin="Germany",
        )
        assert item.name == "Spectrophotometer UV-VIS"
        assert item.model_number == "SP-2000"

    def test_item_with_full_details(self):
        """Test item with all fields."""
        item = EquipmentItem(
            name="HPLC System",
            description="High Performance Liquid Chromatography System",
            model_number="HPLC-3500",
            manufacturer="ChemAnalytics",
            country_of_origin="USA",
            pricing=PriceBreakdown(
                unit_price=Decimal("85000"),
                quantity=1,
                currency=Currency.USD,
            ),
            technical_specs=[
                TechnicalSpecification(
                    parameter="Pressure",
                    value="600",
                    unit="bar",
                ),
            ],
            delivery=DeliveryTerms(
                delivery_time_days=60,
                incoterm="FOB",
            ),
            warranty_period="3 years",
            certifications=["CE", "ISO 9001"],
        )

        assert item.name == "HPLC System"
        assert item.pricing.unit_price == Decimal("85000")
        assert len(item.technical_specs) == 1
        assert item.delivery.delivery_time_days == 60
        assert len(item.certifications) == 2


class TestVendorQuoteValidation:
    """Tests for vendor quote validation."""

    def test_valid_quote(self):
        """Test valid vendor quote."""
        quote = VendorQuote(
            vendor_name="TechLab Solutions",
            quote_reference="TLS-Q-2024-001",
            items=[
                EquipmentItem(name="Item 1"),
                EquipmentItem(name="Item 2"),
            ],
        )
        assert quote.vendor_name == "TechLab Solutions"
        assert len(quote.items) == 2

    def test_quote_with_dates(self):
        """Test quote with date fields."""
        quote = VendorQuote(
            vendor_name="Test Vendor",
            quote_date="2024-12-15",
            validity_date="2025-01-15",
        )
        assert quote.quote_date is not None
        assert quote.validity_date is not None


class TestBaseParserMethods:
    """Tests for BaseParser utility methods."""

    class ConcreteParser(BaseParser):
        """Concrete implementation for testing."""

        SUPPORTED_EXTENSIONS = [".test"]

        def parse(self, file_path):
            pass

        def _extract_raw_data(self, file_path):
            return {}

    def test_extract_price_usd(self):
        """Test USD price extraction."""
        parser = self.ConcreteParser()

        price, currency = parser._extract_price("$15,000.00")
        assert price == Decimal("15000.00")
        assert currency == Currency.USD

    def test_extract_price_eur(self):
        """Test EUR price extraction."""
        parser = self.ConcreteParser()

        price, currency = parser._extract_price("€25,500")
        assert price == Decimal("25500")
        assert currency == Currency.EUR

    def test_extract_price_gbp(self):
        """Test GBP price extraction."""
        parser = self.ConcreteParser()

        price, currency = parser._extract_price("£12,345.67")
        assert price == Decimal("12345.67")
        assert currency == Currency.GBP

    def test_extract_delivery_days(self):
        """Test delivery days extraction."""
        parser = self.ConcreteParser()

        assert parser._extract_delivery_days("45 days") == 45
        assert parser._extract_delivery_days("2 weeks") == 14
        assert parser._extract_delivery_days("3 months") == 90
        assert parser._extract_delivery_days("Delivery: 30 days") == 30

    def test_extract_country_of_origin(self):
        """Test country extraction."""
        parser = self.ConcreteParser()

        assert parser._extract_country_of_origin("Country of Origin: Germany") == "Germany"
        assert parser._extract_country_of_origin("Made in USA") == "Usa"
        assert parser._extract_country_of_origin("Origin: Japan") == "Japan"

    def test_extract_incoterm(self):
        """Test incoterm extraction."""
        parser = self.ConcreteParser()

        assert parser._extract_incoterm("FOB Shanghai") == "FOB"
        assert parser._extract_incoterm("CIF Rotterdam") == "CIF"
        assert parser._extract_incoterm("Terms: DDP") == "DDP"

    def test_column_normalization(self):
        """Test column name normalization."""
        parser = self.ConcreteParser()

        assert parser._normalize_column_name("Unit Price (USD)") == "unitpriceusd"
        assert parser._normalize_column_name("Equipment Name") == "equipmentname"
        assert parser._normalize_column_name("Country of Origin") == "countryoforigin"
