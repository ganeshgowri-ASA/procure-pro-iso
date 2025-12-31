"""Tests for Excel parser."""

from decimal import Decimal
from pathlib import Path

import pytest

from procure_pro_iso.parsers.excel_parser import ExcelParser, MultiVendorExcelParser


class TestExcelParser:
    """Tests for ExcelParser."""

    def test_can_parse_excel(self):
        """Test that parser can identify Excel files."""
        parser = ExcelParser()
        assert parser.can_parse("test.xlsx") is True
        assert parser.can_parse("test.xls") is True
        assert parser.can_parse("test.csv") is False
        assert parser.can_parse("test.pdf") is False

    def test_parse_sample_excel(self, sample_excel_path: Path):
        """Test parsing the sample Excel file."""
        parser = ExcelParser()
        result = parser.parse(sample_excel_path)

        assert result.success is True
        assert result.source_type == "excel"
        assert result.document is not None
        assert len(result.parsing_errors) == 0

    def test_parse_extracts_items(self, sample_excel_path: Path):
        """Test that equipment items are extracted from Excel."""
        parser = ExcelParser()
        result = parser.parse(sample_excel_path)

        assert result.document is not None
        total_items = sum(
            len(quote.items) for quote in result.document.vendor_quotes
        )
        assert total_items > 0

    def test_parse_extracts_prices(self, sample_excel_path: Path):
        """Test that prices are extracted correctly from Excel."""
        parser = ExcelParser()
        result = parser.parse(sample_excel_path)

        assert result.document is not None
        price_found = False
        for quote in result.document.vendor_quotes:
            for item in quote.items:
                if item.pricing and item.pricing.unit_price:
                    price_found = True
                    assert item.pricing.unit_price > 0
        assert price_found

    def test_parse_extracts_delivery(self, sample_excel_path: Path):
        """Test that delivery time is extracted from Excel."""
        parser = ExcelParser()
        result = parser.parse(sample_excel_path)

        assert result.document is not None
        delivery_found = False
        for quote in result.document.vendor_quotes:
            for item in quote.items:
                if item.delivery and item.delivery.delivery_time_days:
                    delivery_found = True
                    assert item.delivery.delivery_time_days > 0
        assert delivery_found

    def test_parse_extracts_country_of_origin(self, sample_excel_path: Path):
        """Test that country of origin is extracted from Excel."""
        parser = ExcelParser()
        result = parser.parse(sample_excel_path)

        assert result.document is not None
        country_found = False
        for quote in result.document.vendor_quotes:
            for item in quote.items:
                if item.country_of_origin:
                    country_found = True
                    break
        assert country_found

    def test_parse_nonexistent_file(self, fixtures_dir: Path):
        """Test parsing a non-existent Excel file."""
        parser = ExcelParser()
        result = parser.parse(fixtures_dir / "nonexistent.xlsx")

        assert result.success is False
        assert len(result.parsing_errors) > 0
        assert result.parsing_errors[0].error_type == "FileNotFound"

    def test_metadata_includes_sheets(self, sample_excel_path: Path):
        """Test that metadata includes processed sheets."""
        parser = ExcelParser()
        result = parser.parse(sample_excel_path)

        assert "sheets_processed" in result.metadata
        assert len(result.metadata["sheets_processed"]) > 0


class TestMultiVendorExcelParser:
    """Tests for MultiVendorExcelParser."""

    def test_parse_multi_sheet_excel(self, multi_vendor_excel_path: Path):
        """Test parsing Excel with vendor sheets."""
        parser = MultiVendorExcelParser(vendor_mode="sheets")
        result = parser.parse(multi_vendor_excel_path)

        assert result.success is True
        assert result.document is not None

        # Should have multiple vendor quotes (one per sheet)
        vendor_quotes = result.document.vendor_quotes
        assert len(vendor_quotes) >= 2

    def test_vendor_mode_auto(self, multi_vendor_excel_path: Path):
        """Test auto-detection of vendor structure."""
        parser = MultiVendorExcelParser(vendor_mode="auto")
        result = parser.parse(multi_vendor_excel_path)

        assert result.success is True
        assert result.document is not None
        assert len(result.document.vendor_quotes) >= 1

    def test_each_vendor_has_items(self, multi_vendor_excel_path: Path):
        """Test that each vendor sheet produces items."""
        parser = MultiVendorExcelParser(vendor_mode="sheets")
        result = parser.parse(multi_vendor_excel_path)

        assert result.document is not None
        for quote in result.document.vendor_quotes:
            assert len(quote.items) > 0


class TestExcelParserEdgeCases:
    """Tests for edge cases in Excel parsing."""

    def test_unsupported_extension(self, fixtures_dir: Path):
        """Test parsing unsupported file extension."""
        parser = ExcelParser()
        # Try to parse a CSV as Excel
        result = parser.parse(fixtures_dir / "sample_rfq.csv")

        assert result.success is False
        assert len(result.parsing_errors) > 0
        assert "UnsupportedFormat" in result.parsing_errors[0].error_type

    def test_with_header_row_specified(self, sample_excel_path: Path):
        """Test parsing with specific header row."""
        parser = ExcelParser(header_row=0)
        result = parser.parse(sample_excel_path)

        assert result.document is not None

    def test_strict_mode_on_errors(self, fixtures_dir: Path):
        """Test strict mode behavior."""
        parser = ExcelParser(strict_mode=True)
        result = parser.parse(fixtures_dir / "nonexistent.xlsx")

        assert result.success is False


class TestColumnMapping:
    """Tests for column name mapping."""

    def test_equipment_name_mapping(self):
        """Test mapping of equipment/item columns."""
        parser = ExcelParser()

        assert parser._map_column_to_field("Equipment Name") == "equipment_name"
        assert parser._map_column_to_field("Item Description") == "equipment_name"
        assert parser._map_column_to_field("Product") == "equipment_name"
        assert parser._map_column_to_field("Material") == "equipment_name"

    def test_vendor_mapping(self):
        """Test mapping of vendor columns."""
        parser = ExcelParser()

        assert parser._map_column_to_field("Vendor") == "vendor_name"
        assert parser._map_column_to_field("Supplier Name") == "vendor_name"
        assert parser._map_column_to_field("Company") == "vendor_name"
        assert parser._map_column_to_field("Manufacturer") == "vendor_name"

    def test_price_mapping(self):
        """Test mapping of price columns."""
        parser = ExcelParser()

        assert parser._map_column_to_field("Unit Price") == "unit_price"
        assert parser._map_column_to_field("Price") == "unit_price"
        assert parser._map_column_to_field("Cost") == "unit_price"
        assert parser._map_column_to_field("Total Price") == "total_price"

    def test_delivery_mapping(self):
        """Test mapping of delivery columns."""
        parser = ExcelParser()

        assert parser._map_column_to_field("Delivery Time") == "delivery_time"
        assert parser._map_column_to_field("Lead Time") == "delivery_time"

    def test_country_mapping(self):
        """Test mapping of country columns."""
        parser = ExcelParser()

        assert parser._map_column_to_field("Country of Origin") == "country_of_origin"
        assert parser._map_column_to_field("Origin") == "country_of_origin"
        assert parser._map_column_to_field("Made In") == "country_of_origin"

    def test_model_mapping(self):
        """Test mapping of model number columns."""
        parser = ExcelParser()

        assert parser._map_column_to_field("Model Number") == "model_number"
        assert parser._map_column_to_field("Part Number") == "model_number"
        assert parser._map_column_to_field("SKU") == "model_number"

    def test_unknown_column(self):
        """Test that unknown columns return None."""
        parser = ExcelParser()

        assert parser._map_column_to_field("Random Column") is None
        assert parser._map_column_to_field("XYZ") is None
