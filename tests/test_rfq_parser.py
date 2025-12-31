"""Tests for unified RFQ parser."""

from pathlib import Path

import pytest

from procure_pro_iso.parsers.rfq_parser import (
    RFQParser,
    parse_rfq,
    parse_rfq_to_dict,
    parse_rfq_to_json,
)


class TestRFQParser:
    """Tests for RFQParser unified interface."""

    def test_parser_initialization(self):
        """Test parser initialization with options."""
        parser = RFQParser()
        assert parser.strict_mode is False
        assert parser.enable_ocr is True
        assert parser.multi_vendor_mode is True

        parser = RFQParser(
            strict_mode=True,
            enable_ocr=False,
            multi_vendor_mode=False,
        )
        assert parser.strict_mode is True
        assert parser.enable_ocr is False
        assert parser.multi_vendor_mode is False

    def test_supported_formats(self):
        """Test that all expected formats are supported."""
        parser = RFQParser()
        formats = parser.supported_formats

        assert ".xlsx" in formats
        assert ".xls" in formats
        assert ".pdf" in formats
        assert ".csv" in formats
        assert ".tsv" in formats

    def test_get_parser_for_extension(self):
        """Test getting parser for specific extension."""
        parser = RFQParser()

        excel_parser = parser.get_parser(".xlsx")
        assert excel_parser is not None

        pdf_parser = parser.get_parser(".pdf")
        assert pdf_parser is not None

        csv_parser = parser.get_parser(".csv")
        assert csv_parser is not None

        unknown_parser = parser.get_parser(".unknown")
        assert unknown_parser is None

    def test_parse_csv_file(self, sample_csv_path: Path):
        """Test parsing CSV file through unified interface."""
        parser = RFQParser()
        result = parser.parse(sample_csv_path)

        assert result.success is True
        assert result.source_type == "csv"
        assert result.document is not None

    def test_parse_excel_file(self, sample_excel_path: Path):
        """Test parsing Excel file through unified interface."""
        parser = RFQParser()
        result = parser.parse(sample_excel_path)

        assert result.success is True
        assert result.source_type == "excel"
        assert result.document is not None

    def test_parse_nonexistent_file(self, fixtures_dir: Path):
        """Test parsing non-existent file."""
        parser = RFQParser()
        result = parser.parse(fixtures_dir / "nonexistent.xlsx")

        assert result.success is False
        assert len(result.parsing_errors) > 0

    def test_parse_unsupported_format(self, temp_dir: Path):
        """Test parsing unsupported file format."""
        # Create a file with unsupported extension
        unsupported = temp_dir / "test.xyz"
        unsupported.write_text("test content")

        parser = RFQParser()
        result = parser.parse(unsupported)

        assert result.success is False
        assert "UnsupportedFormat" in result.parsing_errors[0].error_type

    def test_parse_multiple_files(
        self, sample_csv_path: Path, multi_vendor_csv_path: Path
    ):
        """Test parsing multiple files."""
        parser = RFQParser()
        results = parser.parse_multiple([sample_csv_path, multi_vendor_csv_path])

        assert len(results) == 2
        assert all(r.success for r in results)

    def test_merge_results(
        self, sample_csv_path: Path, multi_vendor_csv_path: Path
    ):
        """Test merging multiple parsing results."""
        parser = RFQParser()
        results = parser.parse_multiple([sample_csv_path, multi_vendor_csv_path])
        merged = parser.merge_results(results)

        assert merged.source_type == "merged"
        assert merged.document is not None
        assert len(merged.document.vendor_quotes) > 0
        assert "source_files" in merged.metadata

    def test_merge_empty_results(self):
        """Test merging empty results list."""
        parser = RFQParser()
        merged = parser.merge_results([])

        assert merged.success is False
        assert len(merged.parsing_errors) > 0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_parse_rfq_function(self, sample_csv_path: Path):
        """Test parse_rfq convenience function."""
        result = parse_rfq(sample_csv_path)

        assert result.success is True
        assert result.document is not None

    def test_parse_rfq_with_options(self, sample_csv_path: Path):
        """Test parse_rfq with custom options."""
        result = parse_rfq(
            sample_csv_path,
            strict_mode=False,
            enable_ocr=False,
            multi_vendor_mode=True,
        )

        assert result.success is True

    def test_parse_rfq_to_json(self, sample_csv_path: Path):
        """Test parse_rfq_to_json function."""
        json_str = parse_rfq_to_json(sample_csv_path)

        assert isinstance(json_str, str)
        assert '"success"' in json_str
        assert '"document"' in json_str

    def test_parse_rfq_to_json_with_indent(self, sample_csv_path: Path):
        """Test parse_rfq_to_json with custom indent."""
        json_str = parse_rfq_to_json(sample_csv_path, indent=4)

        assert isinstance(json_str, str)
        # With indent=4, should have 4-space indentation
        assert "    " in json_str

    def test_parse_rfq_to_dict(self, sample_csv_path: Path):
        """Test parse_rfq_to_dict function."""
        data = parse_rfq_to_dict(sample_csv_path)

        assert isinstance(data, dict)
        assert "success" in data
        assert "document" in data
        assert data["success"] is True


class TestRFQParserIntegration:
    """Integration tests for RFQ parser."""

    def test_full_parsing_workflow(self, sample_csv_path: Path):
        """Test complete parsing workflow."""
        # Parse file
        result = parse_rfq(sample_csv_path)
        assert result.success is True

        # Access document
        doc = result.document
        assert doc is not None

        # Check vendor quotes
        assert len(doc.vendor_quotes) > 0

        # Check items
        for quote in doc.vendor_quotes:
            assert quote.vendor_name
            assert len(quote.items) >= 0

            for item in quote.items:
                assert item.name

    def test_json_export_roundtrip(self, sample_csv_path: Path):
        """Test that JSON export produces valid JSON."""
        import json

        json_str = parse_rfq_to_json(sample_csv_path)
        data = json.loads(json_str)

        assert data["success"] is True
        assert "document" in data
        assert "vendor_quotes" in data["document"]

    def test_extracted_data_types(self, sample_csv_path: Path):
        """Test that extracted data has correct types."""
        result = parse_rfq(sample_csv_path)

        for quote in result.document.vendor_quotes:
            assert isinstance(quote.vendor_name, str)

            for item in quote.items:
                assert isinstance(item.name, str)

                if item.pricing:
                    assert item.pricing.unit_price >= 0
                    assert item.pricing.quantity >= 1

                if item.country_of_origin:
                    assert isinstance(item.country_of_origin, str)

                if item.delivery and item.delivery.delivery_time_days:
                    assert item.delivery.delivery_time_days > 0
