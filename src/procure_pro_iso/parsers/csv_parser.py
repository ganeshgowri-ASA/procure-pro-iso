"""
CSV file parser for RFQ documents.

Handles structured CSV data import with delimiter detection and encoding support.
"""

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from procure_pro_iso.models.rfq import (
    EquipmentItem,
    ParsedRFQResult,
    RFQDocument,
    VendorQuote,
)
from procure_pro_iso.parsers.base import BaseParser


class CSVParser(BaseParser):
    """Parser for CSV files."""

    SUPPORTED_EXTENSIONS = [".csv", ".tsv", ".txt"]

    def __init__(
        self,
        strict_mode: bool = False,
        delimiter: str | None = None,
        encoding: str | None = None,
        has_header: bool = True,
        vendor_column: str | None = None,
    ):
        """
        Initialize the CSV parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
            delimiter: CSV delimiter. If None, auto-detect.
            encoding: File encoding. If None, auto-detect.
            has_header: If True, first row is treated as header.
            vendor_column: Column name containing vendor names.
        """
        super().__init__(strict_mode)
        self.delimiter = delimiter
        self.encoding = encoding
        self.has_header = has_header
        self.vendor_column = vendor_column

    def parse(self, file_path: str | Path) -> ParsedRFQResult:
        """
        Parse a CSV file and extract RFQ data.

        Args:
            file_path: Path to the CSV file.

        Returns:
            ParsedRFQResult containing the extracted data.
        """
        file_path = Path(file_path)
        self.errors = []
        self.validation_errors = []

        if not file_path.exists():
            self._add_error("FileNotFound", f"File not found: {file_path}")
            return self._create_result(file_path, "csv")

        if not self.can_parse(file_path):
            self._add_error(
                "UnsupportedFormat",
                f"Unsupported file format: {file_path.suffix}",
            )
            return self._create_result(file_path, "csv")

        try:
            raw_data = self._extract_raw_data(file_path)
            document = self._process_raw_data(raw_data, file_path)

            return self._create_result(
                file_path,
                "csv",
                document=document,
                raw_data=raw_data,
                metadata={
                    "delimiter": raw_data.get("delimiter"),
                    "encoding": raw_data.get("encoding"),
                    "total_rows": len(raw_data.get("rows", [])),
                    "columns": raw_data.get("columns", []),
                },
            )
        except Exception as e:
            self._add_error("ParsingError", str(e))
            return self._create_result(file_path, "csv")

    def _extract_raw_data(self, file_path: Path) -> dict[str, Any]:
        """
        Extract raw data from CSV file.

        Args:
            file_path: Path to the CSV file.

        Returns:
            Dictionary containing extracted data.
        """
        # Detect encoding if not specified
        encoding = self.encoding or self._detect_encoding(file_path)

        # Detect delimiter if not specified
        delimiter = self.delimiter or self._detect_delimiter(file_path, encoding)

        # Read CSV with pandas
        try:
            df = pd.read_csv(
                file_path,
                delimiter=delimiter,
                encoding=encoding,
                header=0 if self.has_header else None,
                dtype=str,  # Read all as strings initially
                skip_blank_lines=True,
            )
        except Exception as e:
            # Fallback to Python csv reader
            df = self._read_with_csv_module(file_path, encoding, delimiter)

        if df.empty:
            return {
                "columns": [],
                "rows": [],
                "delimiter": delimiter,
                "encoding": encoding,
            }

        # Clean column names
        if self.has_header:
            df.columns = [
                str(col).strip() if pd.notna(col) else f"Column_{i}"
                for i, col in enumerate(df.columns)
            ]
        else:
            df.columns = [f"Column_{i}" for i in range(len(df.columns))]

        # Map columns to standard fields
        column_mapping = self._detect_column_mapping(df.columns.tolist())

        # Extract rows as dictionaries
        rows = []
        for idx, row in df.iterrows():
            row_data = {}
            for col_name, field_name in column_mapping.items():
                value = row.get(col_name)
                if pd.notna(value) and str(value).strip():
                    row_data[field_name] = str(value).strip()

            # Include unmapped columns for technical specs
            for col in df.columns:
                if col not in column_mapping:
                    value = row.get(col)
                    if pd.notna(value) and str(value).strip():
                        if "specs" not in row_data:
                            row_data["specs"] = {}
                        row_data["specs"][col] = str(value).strip()

            if row_data:
                row_data["_row_index"] = idx
                rows.append(row_data)

        return {
            "columns": df.columns.tolist(),
            "column_mapping": column_mapping,
            "rows": rows,
            "dataframe": df,
            "delimiter": delimiter,
            "encoding": encoding,
        }

    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding.

        Args:
            file_path: Path to the file.

        Returns:
            Detected encoding name.
        """
        # Try common encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    f.read(1024)
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue

        return "utf-8"

    def _detect_delimiter(self, file_path: Path, encoding: str) -> str:
        """
        Detect CSV delimiter.

        Args:
            file_path: Path to the file.
            encoding: File encoding.

        Returns:
            Detected delimiter character.
        """
        # Use filename extension hint
        if file_path.suffix.lower() == ".tsv":
            return "\t"

        try:
            with open(file_path, "r", encoding=encoding) as f:
                sample = f.read(4096)

            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            return dialect.delimiter
        except Exception:
            # Default to comma
            return ","

    def _read_with_csv_module(
        self, file_path: Path, encoding: str, delimiter: str
    ) -> pd.DataFrame:
        """
        Fallback CSV reading using Python csv module.

        Args:
            file_path: Path to the file.
            encoding: File encoding.
            delimiter: CSV delimiter.

        Returns:
            DataFrame with parsed data.
        """
        rows = []
        with open(file_path, "r", encoding=encoding, newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if any(cell.strip() for cell in row):
                    rows.append(row)

        if not rows:
            return pd.DataFrame()

        if self.has_header and rows:
            columns = rows[0]
            data = rows[1:]
            return pd.DataFrame(data, columns=columns)
        else:
            return pd.DataFrame(rows)

    def _detect_column_mapping(self, columns: list[str]) -> dict[str, str]:
        """
        Detect mapping from column names to standard field names.

        Args:
            columns: List of column names from the CSV file.

        Returns:
            Dictionary mapping original column names to standard field names.
        """
        mapping = {}
        for col in columns:
            field = self._map_column_to_field(col)
            if field:
                mapping[col] = field
        return mapping

    def _process_raw_data(
        self, raw_data: dict[str, Any], file_path: Path
    ) -> RFQDocument:
        """
        Process raw extracted data into RFQ document structure.

        Args:
            raw_data: Raw data extracted from CSV.
            file_path: Original file path.

        Returns:
            RFQDocument containing structured data.
        """
        rows = raw_data.get("rows", [])
        vendor_quotes = []

        # Check if vendor column exists
        vendor_field = None
        column_mapping = raw_data.get("column_mapping", {})

        if self.vendor_column:
            vendor_field = self.vendor_column
        else:
            for col, field in column_mapping.items():
                if field == "vendor_name":
                    vendor_field = "vendor_name"
                    break

        if vendor_field:
            # Group by vendor
            vendor_quotes = self._extract_vendors_from_rows(rows, vendor_field)
        else:
            # Single vendor
            items = self._build_items_from_rows(rows)
            if items:
                vendor_quotes.append(
                    self._build_vendor_quote("Unknown Vendor", items)
                )

        return RFQDocument(
            rfq_number=self._extract_rfq_number(file_path),
            vendor_quotes=vendor_quotes,
        )

    def _extract_vendors_from_rows(
        self, rows: list[dict[str, Any]], vendor_field: str
    ) -> list[VendorQuote]:
        """
        Extract vendor quotes when vendors are in rows.

        Args:
            rows: List of row data dictionaries.
            vendor_field: Field name containing vendor names.

        Returns:
            List of VendorQuote objects.
        """
        vendors_data: dict[str, list[dict[str, Any]]] = {}

        for row in rows:
            vendor_name = row.get(vendor_field, "Unknown Vendor")
            if not vendor_name or str(vendor_name).strip() == "":
                vendor_name = "Unknown Vendor"
            vendor_name = str(vendor_name).strip()

            if vendor_name not in vendors_data:
                vendors_data[vendor_name] = []
            vendors_data[vendor_name].append(row)

        vendor_quotes = []
        for vendor_name, vendor_rows in vendors_data.items():
            items = self._build_items_from_rows(vendor_rows)
            if items:
                vendor_quotes.append(
                    self._build_vendor_quote(vendor_name, items)
                )

        return vendor_quotes

    def _build_items_from_rows(
        self, rows: list[dict[str, Any]]
    ) -> list[EquipmentItem]:
        """
        Build equipment items from row data.

        Args:
            rows: List of row data dictionaries.

        Returns:
            List of EquipmentItem objects.
        """
        items = []
        for row in rows:
            # Get equipment name
            equipment_name = row.get("equipment_name")
            if not equipment_name:
                equipment_name = row.get("description", "")

            if not equipment_name or str(equipment_name).strip() == "":
                continue

            try:
                item = self._build_equipment_item(str(equipment_name).strip(), row)
                items.append(item)
            except Exception as e:
                self._add_validation_error(
                    "equipment_item",
                    f"Failed to build item: {e}",
                    row=row.get("_row_index"),
                )

        return items

    def _extract_rfq_number(self, file_path: Path) -> str | None:
        """Extract RFQ number from filename."""
        import re

        filename = file_path.stem
        match = re.search(r"RFQ[_\-\s]?(\d+)", filename, re.IGNORECASE)
        if match:
            return f"RFQ-{match.group(1)}"
        return None


class MultiVendorCSVParser(CSVParser):
    """
    Specialized CSV parser for files with multiple vendors.

    Handles various multi-vendor CSV formats.
    """

    def __init__(
        self,
        strict_mode: bool = False,
        delimiter: str | None = None,
        encoding: str | None = None,
        vendor_column: str | None = None,
        group_by_vendor: bool = True,
    ):
        """
        Initialize the multi-vendor CSV parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
            delimiter: CSV delimiter. If None, auto-detect.
            encoding: File encoding. If None, auto-detect.
            vendor_column: Column name containing vendor names.
            group_by_vendor: If True, group items by vendor.
        """
        super().__init__(
            strict_mode=strict_mode,
            delimiter=delimiter,
            encoding=encoding,
            vendor_column=vendor_column,
        )
        self.group_by_vendor = group_by_vendor

    def _process_raw_data(
        self, raw_data: dict[str, Any], file_path: Path
    ) -> RFQDocument:
        """Process raw data with multi-vendor awareness."""
        rows = raw_data.get("rows", [])
        vendor_quotes = []

        if self.group_by_vendor:
            # Try to find vendor column
            column_mapping = raw_data.get("column_mapping", {})
            vendor_field = self.vendor_column or "vendor_name"

            # Check if vendor field exists in any row
            has_vendor = any(vendor_field in row for row in rows)

            if has_vendor:
                vendor_quotes = self._extract_vendors_from_rows(rows, vendor_field)
            else:
                # Try to auto-detect vendor structure
                vendor_quotes = self._auto_detect_vendors(rows, raw_data)
        else:
            items = self._build_items_from_rows(rows)
            if items:
                vendor_quotes.append(
                    self._build_vendor_quote("Unknown Vendor", items)
                )

        return RFQDocument(
            rfq_number=self._extract_rfq_number(file_path),
            vendor_quotes=vendor_quotes,
        )

    def _auto_detect_vendors(
        self, rows: list[dict[str, Any]], raw_data: dict[str, Any]
    ) -> list[VendorQuote]:
        """
        Auto-detect vendor structure in CSV data.

        Args:
            rows: List of row data.
            raw_data: Full raw data including column info.

        Returns:
            List of VendorQuote objects.
        """
        # Look for a column that might contain vendor names
        potential_vendor_cols = []
        columns = raw_data.get("columns", [])

        for col in columns:
            normalized = self._normalize_column_name(col)
            if any(
                x in normalized
                for x in ["vendor", "supplier", "company", "manufacturer"]
            ):
                potential_vendor_cols.append(col)

        if potential_vendor_cols:
            # Use first potential vendor column
            vendor_col = potential_vendor_cols[0]
            # Update rows to include vendor_name from this column
            for row in rows:
                specs = row.get("specs", {})
                if vendor_col in specs:
                    row["vendor_name"] = specs[vendor_col]

            return self._extract_vendors_from_rows(rows, "vendor_name")

        # No vendor column found - create single vendor
        items = self._build_items_from_rows(rows)
        if items:
            return [self._build_vendor_quote("Unknown Vendor", items)]

        return []
