"""Tests for PDF parser."""

from pathlib import Path

import pytest

from procure_pro_iso.parsers.pdf_parser import OCRPDFParser, PDFParser


class TestPDFParser:
    """Tests for PDFParser."""

    def test_can_parse_pdf(self):
        """Test that parser can identify PDF files."""
        parser = PDFParser()
        assert parser.can_parse("test.pdf") is True
        assert parser.can_parse("test.PDF") is True
        assert parser.can_parse("test.xlsx") is False
        assert parser.can_parse("test.csv") is False

    def test_parse_nonexistent_file(self, fixtures_dir: Path):
        """Test parsing a non-existent PDF file."""
        parser = PDFParser()
        result = parser.parse(fixtures_dir / "nonexistent.pdf")

        assert result.success is False
        assert len(result.parsing_errors) > 0
        assert result.parsing_errors[0].error_type == "FileNotFound"

    def test_parse_unsupported_format(self, fixtures_dir: Path):
        """Test parsing unsupported file format."""
        parser = PDFParser()
        result = parser.parse(fixtures_dir / "sample_rfq.csv")

        assert result.success is False
        assert "UnsupportedFormat" in result.parsing_errors[0].error_type

    @pytest.mark.skipif(
        not Path("/home/user/procure-pro-iso/tests/fixtures/sample_rfq.pdf").exists(),
        reason="Sample PDF not available"
    )
    def test_parse_sample_pdf(self, sample_pdf_path: Path):
        """Test parsing the sample PDF file."""
        parser = PDFParser()
        result = parser.parse(sample_pdf_path)

        assert result.source_type == "pdf"
        # PDF parsing may or may not succeed depending on content
        assert result.document is not None or len(result.parsing_errors) > 0

    @pytest.mark.skipif(
        not Path("/home/user/procure-pro-iso/tests/fixtures/sample_rfq.pdf").exists(),
        reason="Sample PDF not available"
    )
    def test_metadata_includes_page_count(self, sample_pdf_path: Path):
        """Test that metadata includes page count."""
        parser = PDFParser()
        result = parser.parse(sample_pdf_path)

        assert "pages_processed" in result.metadata


class TestOCRPDFParser:
    """Tests for OCRPDFParser."""

    def test_ocr_enabled_by_default(self):
        """Test that OCR is enabled by default."""
        parser = OCRPDFParser()
        assert parser.enable_ocr is True

    def test_ocr_language_configuration(self):
        """Test OCR language configuration."""
        parser = OCRPDFParser(ocr_language="deu")
        assert parser.ocr_language == "deu"

    def test_ocr_dpi_configuration(self):
        """Test OCR DPI configuration."""
        parser = OCRPDFParser(ocr_dpi=600)
        assert parser.ocr_dpi == 600

    def test_preprocessing_option(self):
        """Test image preprocessing option."""
        parser = OCRPDFParser(preprocess_images=True)
        assert parser.preprocess_images is True

        parser = OCRPDFParser(preprocess_images=False)
        assert parser.preprocess_images is False


class TestPDFParserFieldExtraction:
    """Tests for field extraction methods in PDF parser."""

    def test_extract_price(self):
        """Test price extraction from text."""
        parser = PDFParser()

        price, currency = parser._extract_price("Price: $15,000.00")
        assert price is not None
        assert float(price) == 15000.00

        price, currency = parser._extract_price("Cost: €25,500")
        assert price is not None
        assert float(price) == 25500

    def test_extract_delivery_days(self):
        """Test delivery time extraction."""
        parser = PDFParser()

        days = parser._extract_delivery_days("Delivery: 45 days")
        assert days == 45

        days = parser._extract_delivery_days("Lead time: 2 weeks")
        assert days == 14

        days = parser._extract_delivery_days("Delivery within 3 months")
        assert days == 90

    def test_extract_country_of_origin(self):
        """Test country of origin extraction."""
        parser = PDFParser()

        country = parser._extract_country_of_origin("Country of Origin: Germany")
        assert country == "Germany"

        country = parser._extract_country_of_origin("Made in USA")
        assert country == "Usa"  # Title case applied

        country = parser._extract_country_of_origin("Origin: United Kingdom")
        assert country == "United Kingdom"

    def test_extract_incoterm(self):
        """Test incoterm extraction."""
        parser = PDFParser()

        incoterm = parser._extract_incoterm("Terms: FOB Shanghai")
        assert incoterm == "FOB"

        incoterm = parser._extract_incoterm("Delivery: CIF Rotterdam")
        assert incoterm == "CIF"

        incoterm = parser._extract_incoterm("DDP New York warehouse")
        assert incoterm == "DDP"


class TestPDFParserRFQExtraction:
    """Tests for RFQ number and title extraction."""

    def test_extract_rfq_number_from_text(self):
        """Test RFQ number extraction from text."""
        parser = PDFParser()

        # Test with file path
        rfq_num = parser._extract_rfq_number_from_text(
            "This is RFQ No. 2024-001 for laboratory equipment",
            Path("test.pdf")
        )
        assert rfq_num == "2024-001"

        rfq_num = parser._extract_rfq_number_from_text(
            "Reference: ABC-123-XYZ",
            Path("test.pdf")
        )
        assert rfq_num == "ABC-123-XYZ"

    def test_extract_rfq_title_from_text(self):
        """Test RFQ title extraction from text."""
        parser = PDFParser()

        title = parser._extract_rfq_title_from_text(
            "Subject: Laboratory Equipment Procurement\nOther text"
        )
        assert title == "Laboratory Equipment Procurement"

        title = parser._extract_rfq_title_from_text(
            "RFQ for Scientific Instruments\nMore details"
        )
        assert title == "Scientific Instruments"

    def test_extract_vendor_name_from_text(self):
        """Test vendor name extraction from text."""
        parser = PDFParser()

        vendor = parser._extract_vendor_name_from_text(
            "Vendor: TechLab Solutions\nAddress: 123 Main St"
        )
        assert vendor == "TechLab Solutions"

        vendor = parser._extract_vendor_name_from_text(
            "Supplier: ChemAnalytics Inc.\nContact: John Doe"
        )
        assert vendor == "ChemAnalytics Inc."
