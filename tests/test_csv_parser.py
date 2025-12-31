"""Tests for CSV parser."""

from decimal import Decimal
from pathlib import Path

import pytest

from procure_pro_iso.parsers.csv_parser import CSVParser, MultiVendorCSVParser


class TestCSVParser:
    """Tests for CSVParser."""

    def test_can_parse_csv(self):
        """Test that parser can identify CSV files."""
        parser = CSVParser()
        assert parser.can_parse("test.csv") is True
        assert parser.can_parse("test.tsv") is True
        assert parser.can_parse("test.txt") is True
        assert parser.can_parse("test.xlsx") is False
        assert parser.can_parse("test.pdf") is False

    def test_parse_sample_csv(self, sample_csv_path: Path):
        """Test parsing the sample CSV file."""
        parser = CSVParser()
        result = parser.parse(sample_csv_path)

        assert result.success is True
        assert result.source_type == "csv"
        assert result.document is not None
        assert len(result.parsing_errors) == 0

    def test_parse_extracts_vendors(self, sample_csv_path: Path):
        """Test that vendors are extracted from CSV."""
        parser = CSVParser()
        result = parser.parse(sample_csv_path)

        assert result.document is not None
        # The sample CSV has a Vendor column, so items should be grouped
        vendor_quotes = result.document.vendor_quotes
        assert len(vendor_quotes) >= 1

    def test_parse_extracts_items(self, sample_csv_path: Path):
        """Test that equipment items are extracted."""
        parser = CSVParser()
        result = parser.parse(sample_csv_path)

        assert result.document is not None
        total_items = sum(
            len(quote.items) for quote in result.document.vendor_quotes
        )
        assert total_items > 0

    def test_parse_extracts_prices(self, sample_csv_path: Path):
        """Test that prices are extracted correctly."""
        parser = CSVParser()
        result = parser.parse(sample_csv_path)

        assert result.document is not None
        for quote in result.document.vendor_quotes:
            for item in quote.items:
                if item.pricing:
                    assert item.pricing.unit_price > 0

    def test_parse_extracts_delivery(self, sample_csv_path: Path):
        """Test that delivery information is extracted."""
        parser = CSVParser()
        result = parser.parse(sample_csv_path)

        assert result.document is not None
        delivery_found = False
        for quote in result.document.vendor_quotes:
            for item in quote.items:
                if item.delivery and item.delivery.delivery_time_days:
                    delivery_found = True
                    assert item.delivery.delivery_time_days > 0
        assert delivery_found

    def test_parse_extracts_country_of_origin(self, sample_csv_path: Path):
        """Test that country of origin is extracted."""
        parser = CSVParser()
        result = parser.parse(sample_csv_path)

        assert result.document is not None
        country_found = False
        for quote in result.document.vendor_quotes:
            for item in quote.items:
                if item.country_of_origin:
                    country_found = True
                    break
        assert country_found

    def test_parse_nonexistent_file(self, fixtures_dir: Path):
        """Test parsing a non-existent file."""
        parser = CSVParser()
        result = parser.parse(fixtures_dir / "nonexistent.csv")

        assert result.success is False
        assert len(result.parsing_errors) > 0
        assert result.parsing_errors[0].error_type == "FileNotFound"

    def test_parse_with_custom_delimiter(self, temp_dir: Path):
        """Test parsing CSV with custom delimiter."""
        # Create a semicolon-delimited file
        csv_content = "Equipment;Price;Vendor\nSpec;15000;TechLab\n"
        csv_path = temp_dir / "semicolon.csv"
        csv_path.write_text(csv_content)

        parser = CSVParser(delimiter=";")
        result = parser.parse(csv_path)

        assert result.success is True
        assert result.metadata.get("delimiter") == ";"

    def test_metadata_includes_row_count(self, sample_csv_path: Path):
        """Test that metadata includes total row count."""
        parser = CSVParser()
        result = parser.parse(sample_csv_path)

        assert "total_rows" in result.metadata
        assert result.metadata["total_rows"] > 0


class TestMultiVendorCSVParser:
    """Tests for MultiVendorCSVParser."""

    def test_parse_multi_vendor_csv(self, multi_vendor_csv_path: Path):
        """Test parsing multi-vendor CSV file."""
        parser = MultiVendorCSVParser()
        result = parser.parse(multi_vendor_csv_path)

        assert result.success is True
        assert result.document is not None

        # Should have multiple vendor quotes
        vendor_quotes = result.document.vendor_quotes
        assert len(vendor_quotes) >= 2

    def test_vendor_grouping(self, multi_vendor_csv_path: Path):
        """Test that items are grouped by vendor."""
        parser = MultiVendorCSVParser()
        result = parser.parse(multi_vendor_csv_path)

        assert result.document is not None
        vendor_names = [q.vendor_name for q in result.document.vendor_quotes]

        # Each vendor should appear only once
        assert len(vendor_names) == len(set(vendor_names))

    def test_each_vendor_has_items(self, multi_vendor_csv_path: Path):
        """Test that each vendor has at least one item."""
        parser = MultiVendorCSVParser()
        result = parser.parse(multi_vendor_csv_path)

        assert result.document is not None
        for quote in result.document.vendor_quotes:
            assert len(quote.items) > 0


class TestCSVParserEdgeCases:
    """Tests for edge cases in CSV parsing."""

    def test_empty_csv(self, temp_dir: Path):
        """Test parsing an empty CSV file."""
        csv_path = temp_dir / "empty.csv"
        csv_path.write_text("")

        parser = CSVParser()
        result = parser.parse(csv_path)

        # Should handle gracefully
        assert result.document is not None or len(result.parsing_errors) > 0

    def test_headers_only_csv(self, temp_dir: Path):
        """Test parsing CSV with headers only."""
        csv_content = "Equipment Name,Vendor,Price\n"
        csv_path = temp_dir / "headers_only.csv"
        csv_path.write_text(csv_content)

        parser = CSVParser()
        result = parser.parse(csv_path)

        assert result.document is not None
        # Should have no items
        total_items = sum(
            len(q.items) for q in result.document.vendor_quotes
        )
        assert total_items == 0

    def test_missing_columns(self, temp_dir: Path):
        """Test parsing CSV with missing expected columns."""
        csv_content = "Name,Value\nItem1,100\nItem2,200\n"
        csv_path = temp_dir / "missing_cols.csv"
        csv_path.write_text(csv_content)

        parser = CSVParser()
        result = parser.parse(csv_path)

        # Should still parse what it can
        assert result.document is not None

    def test_special_characters(self, temp_dir: Path):
        """Test parsing CSV with special characters."""
        csv_content = '''Equipment Name,Vendor,Price,Country
"Spectrophotometer, Model A","TechLab™ Solutions","$15,000.00",Germany
"HPLC — Advanced","Chem & Analytics","€85,000.00",USA
'''
        csv_path = temp_dir / "special_chars.csv"
        csv_path.write_text(csv_content)

        parser = CSVParser()
        result = parser.parse(csv_path)

        assert result.success is True
        assert result.document is not None

    def test_unicode_content(self, temp_dir: Path):
        """Test parsing CSV with unicode content."""
        csv_content = '''Equipment,Vendor,Country
分光光度計,テックラボ,日本
Spektrometer,Wissenschaft GmbH,Deutschland
'''
        csv_path = temp_dir / "unicode.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        parser = CSVParser()
        result = parser.parse(csv_path)

        assert result.success is True

    def test_tsv_file(self, temp_dir: Path):
        """Test parsing TSV (tab-separated) file."""
        csv_content = "Equipment\tVendor\tPrice\nSpec\tTechLab\t15000\n"
        csv_path = temp_dir / "data.tsv"
        csv_path.write_text(csv_content)

        parser = CSVParser()
        result = parser.parse(csv_path)

        assert result.success is True
        assert result.metadata.get("delimiter") == "\t"
