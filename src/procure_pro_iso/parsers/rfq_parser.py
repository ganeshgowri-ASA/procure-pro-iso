"""
Unified RFQ document parser.

Provides a single interface for parsing RFQ documents in various formats
(Excel, PDF, CSV) with automatic format detection.
"""

from pathlib import Path
from typing import Any

from procure_pro_iso.models.rfq import (
    ParsedRFQResult,
    ParsingError,
    RFQDocument,
    VendorQuote,
)
from procure_pro_iso.parsers.base import BaseParser
from procure_pro_iso.parsers.csv_parser import CSVParser, MultiVendorCSVParser
from procure_pro_iso.parsers.excel_parser import ExcelParser, MultiVendorExcelParser
from procure_pro_iso.parsers.pdf_parser import OCRPDFParser, PDFParser


class RFQParser:
    """
    Unified parser for RFQ documents.

    Automatically detects file format and uses the appropriate parser.
    Supports Excel (.xlsx, .xls), PDF, and CSV files.
    """

    def __init__(
        self,
        strict_mode: bool = False,
        enable_ocr: bool = True,
        multi_vendor_mode: bool = True,
    ):
        """
        Initialize the RFQ parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
            enable_ocr: If True, enable OCR for scanned PDFs.
            multi_vendor_mode: If True, use multi-vendor aware parsers.
        """
        self.strict_mode = strict_mode
        self.enable_ocr = enable_ocr
        self.multi_vendor_mode = multi_vendor_mode

        # Initialize parsers
        self._parsers: dict[str, BaseParser] = {}
        self._register_parsers()

    def _register_parsers(self) -> None:
        """Register available parsers for different file types."""
        # Excel parsers
        if self.multi_vendor_mode:
            excel_parser = MultiVendorExcelParser(strict_mode=self.strict_mode)
        else:
            excel_parser = ExcelParser(strict_mode=self.strict_mode)

        for ext in excel_parser.SUPPORTED_EXTENSIONS:
            self._parsers[ext] = excel_parser

        # PDF parsers
        if self.enable_ocr:
            pdf_parser = OCRPDFParser(strict_mode=self.strict_mode)
        else:
            pdf_parser = PDFParser(
                strict_mode=self.strict_mode, enable_ocr=False
            )

        for ext in pdf_parser.SUPPORTED_EXTENSIONS:
            self._parsers[ext] = pdf_parser

        # CSV parsers
        if self.multi_vendor_mode:
            csv_parser = MultiVendorCSVParser(strict_mode=self.strict_mode)
        else:
            csv_parser = CSVParser(strict_mode=self.strict_mode)

        for ext in csv_parser.SUPPORTED_EXTENSIONS:
            self._parsers[ext] = csv_parser

    def parse(self, file_path: str | Path) -> ParsedRFQResult:
        """
        Parse an RFQ document.

        Automatically detects the file format and uses the appropriate parser.

        Args:
            file_path: Path to the RFQ document.

        Returns:
            ParsedRFQResult containing the extracted data.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return ParsedRFQResult(
                success=False,
                source_file=str(file_path),
                source_type="unknown",
                parsing_errors=[
                    ParsingError(
                        error_type="FileNotFound",
                        message=f"File not found: {file_path}",
                    )
                ],
            )

        # Get parser for file type
        extension = file_path.suffix.lower()
        parser = self._parsers.get(extension)

        if parser is None:
            return ParsedRFQResult(
                success=False,
                source_file=str(file_path),
                source_type="unknown",
                parsing_errors=[
                    ParsingError(
                        error_type="UnsupportedFormat",
                        message=f"Unsupported file format: {extension}. "
                        f"Supported formats: {list(self._parsers.keys())}",
                    )
                ],
            )

        return parser.parse(file_path)

    def parse_multiple(
        self, file_paths: list[str | Path]
    ) -> list[ParsedRFQResult]:
        """
        Parse multiple RFQ documents.

        Args:
            file_paths: List of paths to RFQ documents.

        Returns:
            List of ParsedRFQResult objects.
        """
        results = []
        for path in file_paths:
            result = self.parse(path)
            results.append(result)
        return results

    def merge_results(
        self, results: list[ParsedRFQResult]
    ) -> ParsedRFQResult:
        """
        Merge multiple parsing results into a single result.

        Useful when RFQ data is split across multiple files.

        Args:
            results: List of ParsedRFQResult objects to merge.

        Returns:
            Merged ParsedRFQResult.
        """
        if not results:
            return ParsedRFQResult(
                success=False,
                source_file="",
                source_type="merged",
                parsing_errors=[
                    ParsingError(
                        error_type="NoResults",
                        message="No results to merge",
                    )
                ],
            )

        # Collect all vendor quotes
        all_quotes: list[VendorQuote] = []
        all_errors: list[ParsingError] = []
        all_validation_errors = []
        source_files = []

        for result in results:
            source_files.append(result.source_file)
            all_errors.extend(result.parsing_errors)
            all_validation_errors.extend(result.validation_errors)

            if result.document:
                all_quotes.extend(result.document.vendor_quotes)

        # Merge vendor quotes by vendor name
        merged_quotes = self._merge_vendor_quotes(all_quotes)

        # Create merged document
        merged_document = RFQDocument(
            rfq_number=self._get_first_non_none(
                [r.document.rfq_number for r in results if r.document]
            ),
            rfq_title=self._get_first_non_none(
                [r.document.rfq_title for r in results if r.document]
            ),
            vendor_quotes=merged_quotes,
        )

        return ParsedRFQResult(
            success=len(all_errors) == 0 and len(merged_quotes) > 0,
            document=merged_document,
            source_file="; ".join(source_files),
            source_type="merged",
            parsing_errors=all_errors,
            validation_errors=all_validation_errors,
            metadata={
                "source_files": source_files,
                "total_vendors": len(merged_quotes),
            },
        )

    def _merge_vendor_quotes(
        self, quotes: list[VendorQuote]
    ) -> list[VendorQuote]:
        """
        Merge vendor quotes by vendor name.

        Args:
            quotes: List of vendor quotes to merge.

        Returns:
            List of merged vendor quotes.
        """
        vendors: dict[str, VendorQuote] = {}

        for quote in quotes:
            vendor_name = quote.vendor_name.lower().strip()

            if vendor_name not in vendors:
                vendors[vendor_name] = quote
            else:
                # Merge items
                existing = vendors[vendor_name]
                existing.items.extend(quote.items)

                # Update total if possible
                if quote.total_amount and existing.total_amount:
                    existing.total_amount += quote.total_amount
                elif quote.total_amount:
                    existing.total_amount = quote.total_amount

        return list(vendors.values())

    def _get_first_non_none(self, values: list[Any]) -> Any:
        """Get the first non-None value from a list."""
        for v in values:
            if v is not None:
                return v
        return None

    @property
    def supported_formats(self) -> list[str]:
        """Get list of supported file formats."""
        return list(self._parsers.keys())

    def get_parser(self, extension: str) -> BaseParser | None:
        """
        Get the parser for a specific file extension.

        Args:
            extension: File extension (including dot).

        Returns:
            Parser instance or None if not supported.
        """
        return self._parsers.get(extension.lower())


def parse_rfq(
    file_path: str | Path,
    strict_mode: bool = False,
    enable_ocr: bool = True,
    multi_vendor_mode: bool = True,
) -> ParsedRFQResult:
    """
    Convenience function to parse an RFQ document.

    Args:
        file_path: Path to the RFQ document.
        strict_mode: If True, raise exceptions on validation errors.
        enable_ocr: If True, enable OCR for scanned PDFs.
        multi_vendor_mode: If True, use multi-vendor aware parsers.

    Returns:
        ParsedRFQResult containing the extracted data.

    Example:
        >>> result = parse_rfq("vendor_quotes.xlsx")
        >>> if result.success:
        ...     for quote in result.document.vendor_quotes:
        ...         print(f"{quote.vendor_name}: {quote.total_amount}")
    """
    parser = RFQParser(
        strict_mode=strict_mode,
        enable_ocr=enable_ocr,
        multi_vendor_mode=multi_vendor_mode,
    )
    return parser.parse(file_path)


def parse_rfq_to_json(
    file_path: str | Path,
    indent: int = 2,
    **kwargs: Any,
) -> str:
    """
    Parse an RFQ document and return JSON string.

    Args:
        file_path: Path to the RFQ document.
        indent: JSON indentation level.
        **kwargs: Additional arguments passed to parse_rfq.

    Returns:
        JSON string representation of the parsed result.

    Example:
        >>> json_str = parse_rfq_to_json("vendor_quotes.xlsx")
        >>> print(json_str)
    """
    result = parse_rfq(file_path, **kwargs)
    return result.to_json(indent=indent)


def parse_rfq_to_dict(file_path: str | Path, **kwargs: Any) -> dict[str, Any]:
    """
    Parse an RFQ document and return dictionary.

    Args:
        file_path: Path to the RFQ document.
        **kwargs: Additional arguments passed to parse_rfq.

    Returns:
        Dictionary representation of the parsed result.

    Example:
        >>> data = parse_rfq_to_dict("vendor_quotes.xlsx")
        >>> vendors = data['document']['vendor_quotes']
    """
    result = parse_rfq(file_path, **kwargs)
    return result.to_dict()
