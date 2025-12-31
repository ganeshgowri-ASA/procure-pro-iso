"""
PDF file parser for RFQ documents.

Supports both text-based and scanned PDFs with OCR capabilities.
Uses pdfplumber for text extraction and pytesseract for OCR.
"""

import re
from decimal import Decimal
from pathlib import Path
from typing import Any

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
from procure_pro_iso.parsers.base import BaseParser, FieldPatterns


class PDFParser(BaseParser):
    """Parser for PDF files with OCR support."""

    SUPPORTED_EXTENSIONS = [".pdf"]

    def __init__(
        self,
        strict_mode: bool = False,
        enable_ocr: bool = True,
        ocr_language: str = "eng",
        ocr_dpi: int = 300,
    ):
        """
        Initialize the PDF parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
            enable_ocr: If True, use OCR for scanned/image-based PDFs.
            ocr_language: Tesseract language code for OCR.
            ocr_dpi: DPI for rendering PDF pages for OCR.
        """
        super().__init__(strict_mode)
        self.enable_ocr = enable_ocr
        self.ocr_language = ocr_language
        self.ocr_dpi = ocr_dpi

    def parse(self, file_path: str | Path) -> ParsedRFQResult:
        """
        Parse a PDF file and extract RFQ data.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ParsedRFQResult containing the extracted data.
        """
        file_path = Path(file_path)
        self.errors = []
        self.validation_errors = []

        if not file_path.exists():
            self._add_error("FileNotFound", f"File not found: {file_path}")
            return self._create_result(file_path, "pdf")

        if not self.can_parse(file_path):
            self._add_error(
                "UnsupportedFormat",
                f"Unsupported file format: {file_path.suffix}",
            )
            return self._create_result(file_path, "pdf")

        try:
            raw_data = self._extract_raw_data(file_path)
            document = self._process_raw_data(raw_data, file_path)

            return self._create_result(
                file_path,
                "pdf",
                document=document,
                raw_data=raw_data,
                metadata={
                    "pages_processed": raw_data.get("page_count", 0),
                    "ocr_used": raw_data.get("ocr_used", False),
                    "text_length": len(raw_data.get("full_text", "")),
                },
            )
        except Exception as e:
            self._add_error("ParsingError", str(e))
            return self._create_result(file_path, "pdf")

    def _extract_raw_data(self, file_path: Path) -> dict[str, Any]:
        """
        Extract raw data from PDF file.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Dictionary containing extracted text and metadata.
        """
        import pdfplumber

        raw_data = {
            "pages": [],
            "tables": [],
            "full_text": "",
            "page_count": 0,
            "ocr_used": False,
        }

        with pdfplumber.open(file_path) as pdf:
            raw_data["page_count"] = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages):
                page_data = {
                    "page_number": page_num + 1,
                    "text": "",
                    "tables": [],
                }

                # Try to extract text directly
                text = page.extract_text() or ""

                # If no text found and OCR is enabled, try OCR
                if not text.strip() and self.enable_ocr:
                    text = self._ocr_page(page)
                    if text:
                        raw_data["ocr_used"] = True

                page_data["text"] = text
                raw_data["full_text"] += text + "\n"

                # Extract tables
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if table and any(row for row in table if any(cell for cell in row if cell)):
                            page_data["tables"].append(table)
                            raw_data["tables"].append({
                                "page": page_num + 1,
                                "data": table,
                            })

                raw_data["pages"].append(page_data)

        return raw_data

    def _ocr_page(self, page: Any) -> str:
        """
        Perform OCR on a PDF page.

        Args:
            page: pdfplumber page object.

        Returns:
            Extracted text from OCR.
        """
        try:
            from pdf2image import convert_from_path
            import pytesseract
            from PIL import Image
            import io

            # Convert page to image
            img = page.to_image(resolution=self.ocr_dpi)

            # Convert to PIL Image
            pil_image = img.original

            # Run OCR
            text = pytesseract.image_to_string(
                pil_image,
                lang=self.ocr_language,
            )

            return text
        except ImportError as e:
            self._add_error(
                "OCRDependencyMissing",
                f"OCR dependencies not available: {e}",
            )
            return ""
        except Exception as e:
            self._add_error(
                "OCRError",
                f"OCR failed: {e}",
            )
            return ""

    def _process_raw_data(
        self, raw_data: dict[str, Any], file_path: Path
    ) -> RFQDocument:
        """
        Process raw extracted data into RFQ document structure.

        Args:
            raw_data: Raw data extracted from PDF.
            file_path: Original file path.

        Returns:
            RFQDocument containing structured data.
        """
        full_text = raw_data.get("full_text", "")
        tables = raw_data.get("tables", [])

        # Extract document-level information
        rfq_number = self._extract_rfq_number_from_text(full_text, file_path)
        rfq_title = self._extract_rfq_title_from_text(full_text)

        # Extract vendor quotes
        vendor_quotes = []

        # First, try to extract from tables
        if tables:
            table_vendors = self._extract_vendors_from_tables(tables)
            vendor_quotes.extend(table_vendors)

        # If no vendors from tables, try to extract from text
        if not vendor_quotes:
            text_vendors = self._extract_vendors_from_text(full_text)
            vendor_quotes.extend(text_vendors)

        # If still no vendors, create a single vendor quote with all items
        if not vendor_quotes:
            items = self._extract_items_from_text(full_text)
            if items:
                vendor_name = self._extract_vendor_name_from_text(full_text) or "Unknown Vendor"
                vendor_quotes.append(
                    self._build_vendor_quote(vendor_name, items)
                )

        return RFQDocument(
            rfq_number=rfq_number,
            rfq_title=rfq_title,
            vendor_quotes=vendor_quotes,
        )

    def _extract_rfq_number_from_text(
        self, text: str, file_path: Path
    ) -> str | None:
        """Extract RFQ number from text or filename."""
        # Try text patterns
        patterns = [
            r"RFQ\s*(?:No\.?|Number|#)?\s*:?\s*([A-Z0-9\-/]+)",
            r"(?:Quote|Quotation)\s*(?:No\.?|Number|#)?\s*:?\s*([A-Z0-9\-/]+)",
            r"Reference\s*(?:No\.?|Number|#)?\s*:?\s*([A-Z0-9\-/]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Try filename
        filename = file_path.stem
        match = re.search(r"RFQ[_\-\s]?(\d+)", filename, re.IGNORECASE)
        if match:
            return f"RFQ-{match.group(1)}"

        return None

    def _extract_rfq_title_from_text(self, text: str) -> str | None:
        """Extract RFQ title from text."""
        patterns = [
            r"(?:Subject|Title|Re)[\s:]+(.+?)(?:\n|$)",
            r"RFQ\s+(?:for\s+)?(.+?)(?:\n|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if len(title) > 5 and len(title) < 200:
                    return title

        return None

    def _extract_vendor_name_from_text(self, text: str) -> str | None:
        """Extract vendor name from text."""
        for pattern in FieldPatterns.VENDOR_NAME:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vendor = match.group(1).strip()
                # Clean up
                vendor = re.sub(r"[,;:\.]$", "", vendor)
                if len(vendor) > 2:
                    return vendor
        return None

    def _extract_vendors_from_tables(
        self, tables: list[dict[str, Any]]
    ) -> list[VendorQuote]:
        """
        Extract vendor quotes from PDF tables.

        Args:
            tables: List of table data extracted from PDF.

        Returns:
            List of VendorQuote objects.
        """
        vendor_quotes = []
        vendors_items: dict[str, list[EquipmentItem]] = {}

        for table_info in tables:
            table = table_info.get("data", [])
            if not table or len(table) < 2:
                continue

            # Detect header row
            header = table[0]
            column_mapping = {}
            vendor_col_idx = None

            for idx, col in enumerate(header):
                if col:
                    field = self._map_column_to_field(str(col))
                    if field:
                        column_mapping[idx] = field
                    if field == "vendor_name":
                        vendor_col_idx = idx

            # Extract items from rows
            for row in table[1:]:
                if not row or not any(cell for cell in row if cell):
                    continue

                row_data = {}
                for idx, field in column_mapping.items():
                    if idx < len(row) and row[idx]:
                        row_data[field] = row[idx]

                # Get vendor name
                vendor_name = row_data.get("vendor_name", "Unknown Vendor")
                if not vendor_name or str(vendor_name).strip() == "":
                    vendor_name = "Unknown Vendor"
                vendor_name = str(vendor_name).strip()

                # Get item name
                item_name = row_data.get("equipment_name")
                if not item_name:
                    continue

                try:
                    item = self._build_equipment_item(str(item_name), row_data)
                    if vendor_name not in vendors_items:
                        vendors_items[vendor_name] = []
                    vendors_items[vendor_name].append(item)
                except Exception:
                    pass

        for vendor_name, items in vendors_items.items():
            if items:
                vendor_quotes.append(
                    self._build_vendor_quote(vendor_name, items)
                )

        return vendor_quotes

    def _extract_vendors_from_text(self, text: str) -> list[VendorQuote]:
        """
        Extract vendor quotes from unstructured text.

        Args:
            text: Full text from PDF.

        Returns:
            List of VendorQuote objects.
        """
        vendor_quotes = []

        # Look for vendor sections
        vendor_pattern = r"(?:Vendor|Supplier|Company)[\s:]+([^\n]+)"
        vendor_matches = re.findall(vendor_pattern, text, re.IGNORECASE)

        for vendor_name in vendor_matches:
            vendor_name = vendor_name.strip()
            if len(vendor_name) < 2:
                continue

            # Find section for this vendor
            # Look for text between this vendor and the next
            vendor_idx = text.lower().find(vendor_name.lower())
            if vendor_idx == -1:
                continue

            # Find next vendor or end of text
            next_vendor_idx = len(text)
            for other_vendor in vendor_matches:
                if other_vendor != vendor_name:
                    other_idx = text.lower().find(
                        other_vendor.lower(), vendor_idx + len(vendor_name)
                    )
                    if other_idx != -1 and other_idx < next_vendor_idx:
                        next_vendor_idx = other_idx

            vendor_section = text[vendor_idx:next_vendor_idx]
            items = self._extract_items_from_text(vendor_section)

            if items:
                vendor_quotes.append(
                    self._build_vendor_quote(vendor_name, items)
                )

        return vendor_quotes

    def _extract_items_from_text(self, text: str) -> list[EquipmentItem]:
        """
        Extract equipment items from text.

        Args:
            text: Text to extract items from.

        Returns:
            List of EquipmentItem objects.
        """
        items = []

        # Look for item patterns
        item_patterns = [
            r"(?:Item|Product|Equipment)[\s:#]*\d*[\s:]+([^\n]+)",
            r"(?:\d+[\.\)]\s*)([A-Z][^\n]{10,})",
        ]

        found_items = []
        for pattern in item_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_items.extend(matches)

        for item_name in found_items:
            item_name = item_name.strip()
            if len(item_name) < 3:
                continue

            # Try to find associated price
            price_match = None
            for pattern in FieldPatterns.PRICE:
                match = re.search(pattern, text[text.find(item_name):], re.IGNORECASE)
                if match:
                    price_match = match.group(1)
                    break

            # Try to find delivery time
            delivery_time = None
            for pattern in FieldPatterns.DELIVERY_TIME:
                match = re.search(pattern, text[text.find(item_name):], re.IGNORECASE)
                if match:
                    delivery_time = match.group(0)
                    break

            # Try to find country of origin
            country = self._extract_country_of_origin(text[text.find(item_name):])

            row_data = {}
            if price_match:
                row_data["unit_price"] = price_match
            if delivery_time:
                row_data["delivery_time"] = delivery_time
            if country:
                row_data["country_of_origin"] = country

            try:
                item = self._build_equipment_item(item_name, row_data)
                items.append(item)
            except Exception:
                pass

        return items

    def _extract_technical_specs_from_text(
        self, text: str
    ) -> list[TechnicalSpecification]:
        """
        Extract technical specifications from text.

        Args:
            text: Text to extract specifications from.

        Returns:
            List of TechnicalSpecification objects.
        """
        specs = []

        # Look for specification patterns
        spec_patterns = [
            r"([A-Za-z\s]+):\s*([\d\.]+)\s*([A-Za-z%°]+)",
            r"([A-Za-z\s]+)\s*[=:]\s*([\d\.]+\s*[A-Za-z%°]*)",
        ]

        for pattern in spec_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                param = match[0].strip()
                value = match[1].strip()
                unit = match[2].strip() if len(match) > 2 else None

                if param and value and len(param) > 2:
                    specs.append(
                        TechnicalSpecification(
                            parameter=param,
                            value=value,
                            unit=unit,
                        )
                    )

        return specs


class OCRPDFParser(PDFParser):
    """
    Specialized PDF parser for scanned documents.

    Optimized for OCR processing with image preprocessing.
    """

    def __init__(
        self,
        strict_mode: bool = False,
        ocr_language: str = "eng",
        ocr_dpi: int = 300,
        preprocess_images: bool = True,
    ):
        """
        Initialize the OCR PDF parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
            ocr_language: Tesseract language code for OCR.
            ocr_dpi: DPI for rendering PDF pages for OCR.
            preprocess_images: If True, apply image preprocessing for better OCR.
        """
        super().__init__(
            strict_mode=strict_mode,
            enable_ocr=True,
            ocr_language=ocr_language,
            ocr_dpi=ocr_dpi,
        )
        self.preprocess_images = preprocess_images

    def _ocr_page(self, page: Any) -> str:
        """
        Perform OCR on a PDF page with optional preprocessing.

        Args:
            page: pdfplumber page object.

        Returns:
            Extracted text from OCR.
        """
        try:
            import pytesseract
            from PIL import Image, ImageFilter, ImageEnhance

            # Convert page to image
            img = page.to_image(resolution=self.ocr_dpi)
            pil_image = img.original

            if self.preprocess_images:
                # Convert to grayscale
                pil_image = pil_image.convert("L")

                # Enhance contrast
                enhancer = ImageEnhance.Contrast(pil_image)
                pil_image = enhancer.enhance(2.0)

                # Apply sharpening
                pil_image = pil_image.filter(ImageFilter.SHARPEN)

                # Binarize (threshold)
                threshold = 128
                pil_image = pil_image.point(
                    lambda x: 255 if x > threshold else 0, mode="1"
                )

            # Run OCR with configuration for table/document layout
            custom_config = r"--oem 3 --psm 6"
            text = pytesseract.image_to_string(
                pil_image,
                lang=self.ocr_language,
                config=custom_config,
            )

            return text
        except ImportError as e:
            self._add_error(
                "OCRDependencyMissing",
                f"OCR dependencies not available: {e}",
            )
            return ""
        except Exception as e:
            self._add_error(
                "OCRError",
                f"OCR failed: {e}",
            )
            return ""
