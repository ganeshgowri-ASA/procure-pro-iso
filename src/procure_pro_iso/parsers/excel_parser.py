"""
Excel file parser for RFQ documents.

Supports .xlsx and .xls file formats with multi-sheet and multi-vendor handling.
"""

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

from procure_pro_iso.models.rfq import (
    Currency,
    EquipmentItem,
    ParsedRFQResult,
    RFQDocument,
    VendorQuote,
)
from procure_pro_iso.parsers.base import BaseParser


class ExcelParser(BaseParser):
    """Parser for Excel files (.xlsx, .xls)."""

    SUPPORTED_EXTENSIONS = [".xlsx", ".xls"]

    def __init__(
        self,
        strict_mode: bool = False,
        header_row: int | None = None,
        vendor_column: str | None = None,
    ):
        """
        Initialize the Excel parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
            header_row: Row index (0-based) containing headers.
                       If None, auto-detect.
            vendor_column: Column name containing vendor names.
                          If None, auto-detect or use sheet names.
        """
        super().__init__(strict_mode)
        self.header_row = header_row
        self.vendor_column = vendor_column

    def parse(self, file_path: str | Path) -> ParsedRFQResult:
        """
        Parse an Excel file and extract RFQ data.

        Args:
            file_path: Path to the Excel file.

        Returns:
            ParsedRFQResult containing the extracted data.
        """
        file_path = Path(file_path)
        self.errors = []
        self.validation_errors = []

        if not file_path.exists():
            self._add_error("FileNotFound", f"File not found: {file_path}")
            return self._create_result(file_path, "excel")

        if not self.can_parse(file_path):
            self._add_error(
                "UnsupportedFormat",
                f"Unsupported file format: {file_path.suffix}",
            )
            return self._create_result(file_path, "excel")

        try:
            raw_data = self._extract_raw_data(file_path)
            document = self._process_raw_data(raw_data, file_path)

            return self._create_result(
                file_path,
                "excel",
                document=document,
                raw_data=raw_data,
                metadata={
                    "sheets_processed": list(raw_data.keys()),
                    "total_rows": sum(
                        len(sheet_data.get("rows", []))
                        for sheet_data in raw_data.values()
                    ),
                },
            )
        except Exception as e:
            self._add_error("ParsingError", str(e))
            return self._create_result(file_path, "excel")

    def _extract_raw_data(self, file_path: Path) -> dict[str, Any]:
        """
        Extract raw data from Excel file.

        Args:
            file_path: Path to the Excel file.

        Returns:
            Dictionary with sheet names as keys and extracted data as values.
        """
        # Determine engine based on file extension
        engine = "openpyxl" if file_path.suffix.lower() == ".xlsx" else "xlrd"

        # Read all sheets
        excel_file = pd.ExcelFile(file_path, engine=engine)
        raw_data = {}

        for sheet_name in excel_file.sheet_names:
            try:
                # Read sheet with header detection
                if self.header_row is not None:
                    df = pd.read_excel(
                        excel_file,
                        sheet_name=sheet_name,
                        header=self.header_row,
                    )
                else:
                    df = self._read_with_header_detection(excel_file, sheet_name)

                if df.empty:
                    continue

                # Clean column names
                df.columns = [
                    str(col).strip() if pd.notna(col) else f"Column_{i}"
                    for i, col in enumerate(df.columns)
                ]

                # Map columns to standard fields
                column_mapping = self._detect_column_mapping(df.columns.tolist())

                # Extract rows as dictionaries
                rows = []
                for idx, row in df.iterrows():
                    row_data = {}
                    for col_name, field_name in column_mapping.items():
                        value = row.get(col_name)
                        if pd.notna(value):
                            row_data[field_name] = value
                    # Include unmapped columns for technical specs
                    for col in df.columns:
                        if col not in column_mapping and pd.notna(row.get(col)):
                            if "specs" not in row_data:
                                row_data["specs"] = {}
                            row_data["specs"][col] = row.get(col)
                    if row_data:
                        row_data["_row_index"] = idx
                        rows.append(row_data)

                raw_data[sheet_name] = {
                    "columns": df.columns.tolist(),
                    "column_mapping": column_mapping,
                    "rows": rows,
                    "dataframe": df,
                }
            except Exception as e:
                self._add_error(
                    "SheetParsingError",
                    f"Error parsing sheet '{sheet_name}': {e}",
                    location=sheet_name,
                )

        return raw_data

    def _read_with_header_detection(
        self, excel_file: pd.ExcelFile, sheet_name: str
    ) -> pd.DataFrame:
        """
        Read Excel sheet with automatic header detection.

        Args:
            excel_file: Pandas ExcelFile object.
            sheet_name: Name of the sheet to read.

        Returns:
            DataFrame with properly detected headers.
        """
        # Read first 10 rows to detect header
        preview = pd.read_excel(
            excel_file, sheet_name=sheet_name, header=None, nrows=10
        )

        if preview.empty:
            return pd.DataFrame()

        # Find the row that looks most like a header
        header_row = 0
        max_score = 0

        for idx in range(min(5, len(preview))):
            row = preview.iloc[idx]
            score = 0
            for val in row:
                if pd.isna(val):
                    continue
                val_str = str(val).lower()
                # Score based on common header keywords
                if any(
                    kw in val_str
                    for kw in [
                        "item",
                        "description",
                        "price",
                        "quantity",
                        "vendor",
                        "supplier",
                        "equipment",
                        "unit",
                        "total",
                        "delivery",
                        "model",
                        "part",
                        "spec",
                    ]
                ):
                    score += 2
                # String values are more likely headers
                if isinstance(val, str) and not val.replace(".", "").isdigit():
                    score += 1
            if score > max_score:
                max_score = score
                header_row = idx

        # Read with detected header
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row)

        return df

    def _detect_column_mapping(self, columns: list[str]) -> dict[str, str]:
        """
        Detect mapping from column names to standard field names.

        Args:
            columns: List of column names from the Excel file.

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
            raw_data: Raw data extracted from Excel file.
            file_path: Original file path.

        Returns:
            RFQDocument containing structured data.
        """
        vendor_quotes = []

        # Determine if vendors are in separate sheets or in a column
        if self.vendor_column:
            # Vendors are in a column - process all sheets together
            all_rows = []
            for sheet_data in raw_data.values():
                all_rows.extend(sheet_data.get("rows", []))
            vendor_quotes = self._extract_vendors_from_column(
                all_rows, self.vendor_column
            )
        else:
            # Try to detect vendor structure
            vendor_quotes = self._auto_detect_vendors(raw_data)

        return RFQDocument(
            rfq_number=self._extract_rfq_number(file_path, raw_data),
            rfq_title=self._extract_rfq_title(raw_data),
            vendor_quotes=vendor_quotes,
        )

    def _auto_detect_vendors(
        self, raw_data: dict[str, Any]
    ) -> list[VendorQuote]:
        """
        Auto-detect vendor structure in Excel data.

        Args:
            raw_data: Raw extracted data.

        Returns:
            List of VendorQuote objects.
        """
        vendor_quotes = []

        # Check if vendor column exists in any sheet
        vendor_col = None
        for sheet_data in raw_data.values():
            mapping = sheet_data.get("column_mapping", {})
            for col, field in mapping.items():
                if field == "vendor_name":
                    vendor_col = col
                    break
            if vendor_col:
                break

        if vendor_col:
            # Vendors are in a column
            all_rows = []
            for sheet_data in raw_data.values():
                all_rows.extend(sheet_data.get("rows", []))
            vendor_quotes = self._extract_vendors_from_column(all_rows, "vendor_name")
        else:
            # Treat each sheet as a vendor or combine all data
            if len(raw_data) > 1:
                # Multiple sheets - try sheet names as vendors
                for sheet_name, sheet_data in raw_data.items():
                    rows = sheet_data.get("rows", [])
                    if not rows:
                        continue

                    items = self._build_items_from_rows(rows)
                    if items:
                        # Use sheet name as vendor if it looks like a vendor name
                        vendor_name = sheet_name
                        if sheet_name.lower() in ["sheet1", "data", "items", "quotes"]:
                            vendor_name = "Unknown Vendor"

                        vendor_quotes.append(
                            self._build_vendor_quote(vendor_name, items)
                        )
            else:
                # Single sheet - create single vendor from data
                for sheet_name, sheet_data in raw_data.items():
                    rows = sheet_data.get("rows", [])
                    items = self._build_items_from_rows(rows)
                    if items:
                        vendor_quotes.append(
                            self._build_vendor_quote("Unknown Vendor", items)
                        )

        return vendor_quotes

    def _extract_vendors_from_column(
        self, rows: list[dict[str, Any]], vendor_field: str
    ) -> list[VendorQuote]:
        """
        Extract vendor quotes when vendors are in a column.

        Args:
            rows: List of row data dictionaries.
            vendor_field: Field name containing vendor names.

        Returns:
            List of VendorQuote objects.
        """
        vendor_quotes = []
        vendors_data: dict[str, list[dict[str, Any]]] = {}

        for row in rows:
            vendor_name = row.get(vendor_field, "Unknown Vendor")
            if pd.isna(vendor_name) or not str(vendor_name).strip():
                vendor_name = "Unknown Vendor"
            vendor_name = str(vendor_name).strip()

            if vendor_name not in vendors_data:
                vendors_data[vendor_name] = []
            vendors_data[vendor_name].append(row)

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
            if not equipment_name or (
                isinstance(equipment_name, float) and pd.isna(equipment_name)
            ):
                equipment_name = row.get("description", "Unnamed Item")

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

    def _extract_rfq_number(
        self, file_path: Path, raw_data: dict[str, Any]
    ) -> str | None:
        """Extract RFQ number from filename or data."""
        # Try to extract from filename
        filename = file_path.stem
        import re

        rfq_pattern = r"RFQ[_\-\s]?(\d+)"
        match = re.search(rfq_pattern, filename, re.IGNORECASE)
        if match:
            return f"RFQ-{match.group(1)}"

        return None

    def _extract_rfq_title(self, raw_data: dict[str, Any]) -> str | None:
        """Extract RFQ title from data."""
        # Look for title in first sheet's early rows
        for sheet_data in raw_data.values():
            rows = sheet_data.get("rows", [])
            for row in rows[:3]:  # Check first 3 rows
                for key, value in row.items():
                    if key and "title" in str(key).lower():
                        return str(value)
        return None


class MultiVendorExcelParser(ExcelParser):
    """
    Specialized parser for Excel files with multiple vendors.

    Handles common multi-vendor formats:
    - Vendors in separate columns (side-by-side comparison)
    - Vendors in separate sheets
    - Vendors in a dedicated column
    """

    def __init__(
        self,
        strict_mode: bool = False,
        vendor_mode: str = "auto",
    ):
        """
        Initialize the multi-vendor Excel parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
            vendor_mode: How vendors are organized:
                - "auto": Auto-detect
                - "columns": Vendors in separate columns
                - "sheets": Vendors in separate sheets
                - "rows": Vendors in a column with items in rows
        """
        super().__init__(strict_mode)
        self.vendor_mode = vendor_mode

    def _process_raw_data(
        self, raw_data: dict[str, Any], file_path: Path
    ) -> RFQDocument:
        """Process raw data with multi-vendor awareness."""
        vendor_quotes = []

        if self.vendor_mode == "columns":
            vendor_quotes = self._extract_vendors_from_columns(raw_data)
        elif self.vendor_mode == "sheets":
            vendor_quotes = self._extract_vendors_from_sheets(raw_data)
        elif self.vendor_mode == "rows":
            all_rows = []
            for sheet_data in raw_data.values():
                all_rows.extend(sheet_data.get("rows", []))
            vendor_quotes = self._extract_vendors_from_column(all_rows, "vendor_name")
        else:  # auto
            vendor_quotes = self._auto_detect_vendors(raw_data)

        return RFQDocument(
            rfq_number=self._extract_rfq_number(file_path, raw_data),
            rfq_title=self._extract_rfq_title(raw_data),
            vendor_quotes=vendor_quotes,
        )

    def _extract_vendors_from_columns(
        self, raw_data: dict[str, Any]
    ) -> list[VendorQuote]:
        """
        Extract vendors when they are in separate columns.

        This handles comparison-style spreadsheets where each vendor
        has their own column for price, delivery, etc.
        """
        vendor_quotes = []

        for sheet_data in raw_data.values():
            df = sheet_data.get("dataframe")
            if df is None or df.empty:
                continue

            # Detect vendor columns (columns with prices)
            vendor_columns = []
            for col in df.columns:
                normalized = self._normalize_column_name(col)
                # Look for columns that might be vendor names with prices
                if self._column_contains_prices(df[col]):
                    vendor_columns.append(col)

            if not vendor_columns:
                continue

            # Find item description column
            item_col = None
            for col in df.columns:
                field = self._map_column_to_field(col)
                if field == "equipment_name":
                    item_col = col
                    break

            if not item_col:
                continue

            # Build vendor quotes from columns
            for vendor_col in vendor_columns:
                items = []
                for _, row in df.iterrows():
                    item_name = row.get(item_col)
                    if pd.isna(item_name):
                        continue

                    price_val = row.get(vendor_col)
                    if pd.isna(price_val):
                        continue

                    row_data = {
                        "equipment_name": item_name,
                        "unit_price": price_val,
                    }
                    try:
                        item = self._build_equipment_item(str(item_name), row_data)
                        items.append(item)
                    except Exception:
                        pass

                if items:
                    vendor_quotes.append(
                        self._build_vendor_quote(str(vendor_col), items)
                    )

        return vendor_quotes

    def _extract_vendors_from_sheets(
        self, raw_data: dict[str, Any]
    ) -> list[VendorQuote]:
        """Extract vendors when each sheet represents a vendor."""
        vendor_quotes = []

        for sheet_name, sheet_data in raw_data.items():
            rows = sheet_data.get("rows", [])
            if not rows:
                continue

            items = self._build_items_from_rows(rows)
            if items:
                vendor_quotes.append(
                    self._build_vendor_quote(sheet_name, items)
                )

        return vendor_quotes

    def _column_contains_prices(self, column: pd.Series) -> bool:
        """Check if a column contains price data."""
        non_null = column.dropna()
        if len(non_null) == 0:
            return False

        price_count = 0
        for val in non_null:
            val_str = str(val)
            # Check for currency symbols or numeric values
            if any(c in val_str for c in "$€£¥₹"):
                price_count += 1
            elif val_str.replace(",", "").replace(".", "").isdigit():
                price_count += 1

        return price_count / len(non_null) > 0.5
