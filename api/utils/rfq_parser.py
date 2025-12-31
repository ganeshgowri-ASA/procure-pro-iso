"""
RFQ Parser Module
Utilities for parsing RFQ documents from various formats (PDF, Excel, etc.)
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, date

logger = logging.getLogger(__name__)


@dataclass
class ParsedRFQItem:
    """Represents a parsed RFQ line item."""
    line_number: int
    description: str
    quantity: Decimal
    unit: str = ""
    specifications: str = ""
    target_price: Optional[Decimal] = None
    required_date: Optional[date] = None
    notes: str = ""


@dataclass
class ParsedRFQ:
    """Represents a fully parsed RFQ document."""
    title: str = ""
    description: str = ""
    rfq_number: str = ""
    issue_date: Optional[date] = None
    closing_date: Optional[date] = None
    project_name: str = ""
    client_name: str = ""
    delivery_location: str = ""
    delivery_terms: str = ""
    payment_terms: str = ""
    currency: str = "USD"
    terms_and_conditions: str = ""
    special_instructions: str = ""
    items: List[ParsedRFQItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RFQParser:
    """
    Parser for RFQ documents supporting multiple formats.

    Supports:
    - PDF documents
    - Excel spreadsheets (xlsx, xls)
    - CSV files
    """

    # Common unit patterns
    UNIT_PATTERNS = {
        'EA': r'\b(ea|each|pcs?|pieces?|units?)\b',
        'SET': r'\b(sets?)\b',
        'KG': r'\b(kg|kgs|kilograms?|kilos?)\b',
        'LB': r'\b(lb|lbs|pounds?)\b',
        'M': r'\b(m|meters?|metres?)\b',
        'FT': r'\b(ft|feet|foot)\b',
        'L': r'\b(l|liters?|litres?)\b',
        'BOX': r'\b(box|boxes)\b',
        'LOT': r'\b(lots?)\b',
    }

    # Date patterns
    DATE_PATTERNS = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        r'(\d{1,2}\s+\w+\s+\d{4})',
    ]

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def parse_pdf(self, file_path: str) -> ParsedRFQ:
        """
        Parse an RFQ from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            ParsedRFQ object with extracted data
        """
        try:
            import pdfplumber

            rfq = ParsedRFQ()
            text_content = []

            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

                    # Try to extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        items = self._parse_table_items(table)
                        rfq.items.extend(items)

            # Parse text content for RFQ details
            full_text = '\n'.join(text_content)
            self._extract_rfq_details(full_text, rfq)

            return rfq

        except ImportError:
            self.errors.append("pdfplumber not installed. Install with: pip install pdfplumber")
            return ParsedRFQ()
        except Exception as e:
            self.errors.append(f"Error parsing PDF: {str(e)}")
            logger.error(f"PDF parsing error: {str(e)}")
            return ParsedRFQ()

    def parse_excel(self, file_path: str, sheet_name: Optional[str] = None) -> ParsedRFQ:
        """
        Parse an RFQ from an Excel file.

        Args:
            file_path: Path to the Excel file
            sheet_name: Optional specific sheet to parse

        Returns:
            ParsedRFQ object with extracted data
        """
        try:
            import pandas as pd

            rfq = ParsedRFQ()

            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)

            # Try to identify header row
            header_row = self._find_header_row(df)
            if header_row is not None:
                df = pd.read_excel(file_path, header=header_row)

            # Map columns to expected fields
            column_mapping = self._detect_columns(df.columns.tolist())

            # Extract items
            for idx, row in df.iterrows():
                item = self._parse_excel_row(row, column_mapping, idx + 1)
                if item:
                    rfq.items.append(item)

            return rfq

        except ImportError:
            self.errors.append("pandas/openpyxl not installed")
            return ParsedRFQ()
        except Exception as e:
            self.errors.append(f"Error parsing Excel: {str(e)}")
            logger.error(f"Excel parsing error: {str(e)}")
            return ParsedRFQ()

    def parse_csv(self, file_path: str) -> ParsedRFQ:
        """
        Parse an RFQ from a CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            ParsedRFQ object with extracted data
        """
        try:
            import pandas as pd

            rfq = ParsedRFQ()
            df = pd.read_csv(file_path)

            # Map columns
            column_mapping = self._detect_columns(df.columns.tolist())

            # Extract items
            for idx, row in df.iterrows():
                item = self._parse_excel_row(row, column_mapping, idx + 1)
                if item:
                    rfq.items.append(item)

            return rfq

        except Exception as e:
            self.errors.append(f"Error parsing CSV: {str(e)}")
            return ParsedRFQ()

    def _parse_table_items(self, table: List[List[str]]) -> List[ParsedRFQItem]:
        """Parse items from a table structure."""
        items = []

        if not table or len(table) < 2:
            return items

        # First row is likely headers
        headers = [str(h).lower().strip() if h else '' for h in table[0]]

        # Try to identify column indices
        desc_idx = self._find_column_index(headers, ['description', 'item', 'material', 'product'])
        qty_idx = self._find_column_index(headers, ['quantity', 'qty', 'amount'])
        unit_idx = self._find_column_index(headers, ['unit', 'uom', 'u/m'])
        price_idx = self._find_column_index(headers, ['price', 'rate', 'cost', 'target'])

        for i, row in enumerate(table[1:], start=1):
            try:
                if not row or all(not cell for cell in row):
                    continue

                description = str(row[desc_idx]) if desc_idx is not None and desc_idx < len(row) else ""
                if not description.strip():
                    continue

                quantity = Decimal('1')
                if qty_idx is not None and qty_idx < len(row) and row[qty_idx]:
                    try:
                        quantity = Decimal(str(row[qty_idx]).replace(',', ''))
                    except Exception:
                        pass

                unit = ""
                if unit_idx is not None and unit_idx < len(row) and row[unit_idx]:
                    unit = str(row[unit_idx]).strip()

                target_price = None
                if price_idx is not None and price_idx < len(row) and row[price_idx]:
                    try:
                        price_str = str(row[price_idx]).replace(',', '').replace('$', '')
                        target_price = Decimal(price_str)
                    except Exception:
                        pass

                item = ParsedRFQItem(
                    line_number=i,
                    description=description.strip(),
                    quantity=quantity,
                    unit=unit,
                    target_price=target_price
                )
                items.append(item)

            except Exception as e:
                self.warnings.append(f"Could not parse row {i}: {str(e)}")

        return items

    def _extract_rfq_details(self, text: str, rfq: ParsedRFQ) -> None:
        """Extract RFQ header details from text content."""

        # RFQ Number patterns
        rfq_patterns = [
            r'RFQ\s*(?:No\.?|Number|#)?\s*:?\s*([A-Z0-9\-/]+)',
            r'Request\s+for\s+Quotation\s*:?\s*([A-Z0-9\-/]+)',
            r'Inquiry\s*(?:No\.?|#)?\s*:?\s*([A-Z0-9\-/]+)',
        ]
        for pattern in rfq_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rfq.rfq_number = match.group(1).strip()
                break

        # Project name
        project_patterns = [
            r'Project\s*(?:Name|Title)?\s*:?\s*([^\n]+)',
            r'Job\s*(?:Name|No\.?)?\s*:?\s*([^\n]+)',
        ]
        for pattern in project_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rfq.project_name = match.group(1).strip()
                break

        # Dates
        date_labels = {
            'issue_date': ['issue date', 'date issued', 'rfq date'],
            'closing_date': ['closing date', 'due date', 'submission deadline', 'valid until']
        }
        for attr, labels in date_labels.items():
            for label in labels:
                pattern = rf'{label}\s*:?\s*({"|".join(self.DATE_PATTERNS)})'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parsed_date = self._parse_date(match.group(1))
                    if parsed_date:
                        setattr(rfq, attr, parsed_date)
                    break

        # Delivery location
        delivery_patterns = [
            r'Delivery\s+(?:Location|Address|Point)\s*:?\s*([^\n]+)',
            r'Ship\s+to\s*:?\s*([^\n]+)',
        ]
        for pattern in delivery_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rfq.delivery_location = match.group(1).strip()
                break

        # Payment terms
        payment_patterns = [
            r'Payment\s+Terms?\s*:?\s*([^\n]+)',
            r'Terms\s+of\s+Payment\s*:?\s*([^\n]+)',
        ]
        for pattern in payment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rfq.payment_terms = match.group(1).strip()
                break

    def _find_column_index(self, headers: List[str], keywords: List[str]) -> Optional[int]:
        """Find column index matching any of the keywords."""
        for i, header in enumerate(headers):
            for keyword in keywords:
                if keyword in header.lower():
                    return i
        return None

    def _find_header_row(self, df) -> Optional[int]:
        """Find the row that contains column headers."""
        header_keywords = ['description', 'item', 'quantity', 'qty', 'unit', 'price']

        for idx in range(min(10, len(df))):
            row_values = [str(v).lower() for v in df.iloc[idx].values if v]
            matches = sum(1 for kw in header_keywords if any(kw in v for v in row_values))
            if matches >= 2:
                return idx

        return None

    def _detect_columns(self, columns: List[str]) -> Dict[str, int]:
        """Detect column mappings from column names."""
        mapping = {}
        columns_lower = [str(c).lower() for c in columns]

        column_keywords = {
            'description': ['description', 'item', 'material', 'product', 'name'],
            'quantity': ['quantity', 'qty', 'amount', 'count'],
            'unit': ['unit', 'uom', 'u/m', 'measure'],
            'price': ['price', 'rate', 'cost', 'target', 'estimate'],
            'specifications': ['specifications', 'specs', 'spec', 'details'],
            'delivery_date': ['delivery', 'required', 'date', 'due'],
        }

        for field, keywords in column_keywords.items():
            for i, col in enumerate(columns_lower):
                if any(kw in col for kw in keywords):
                    mapping[field] = i
                    break

        return mapping

    def _parse_excel_row(self, row, column_mapping: Dict[str, int],
                         line_number: int) -> Optional[ParsedRFQItem]:
        """Parse a single Excel row into an RFQItem."""
        try:
            # Get description
            desc_idx = column_mapping.get('description')
            if desc_idx is None:
                return None

            description = str(row.iloc[desc_idx]) if desc_idx < len(row) else ""
            if not description or description.lower() in ['nan', 'none', '']:
                return None

            # Get quantity
            quantity = Decimal('1')
            qty_idx = column_mapping.get('quantity')
            if qty_idx is not None and qty_idx < len(row):
                try:
                    qty_val = row.iloc[qty_idx]
                    if qty_val and str(qty_val).lower() not in ['nan', 'none']:
                        quantity = Decimal(str(qty_val).replace(',', ''))
                except Exception:
                    pass

            # Get unit
            unit = ""
            unit_idx = column_mapping.get('unit')
            if unit_idx is not None and unit_idx < len(row):
                unit_val = row.iloc[unit_idx]
                if unit_val and str(unit_val).lower() not in ['nan', 'none']:
                    unit = str(unit_val).strip()

            # Get price
            target_price = None
            price_idx = column_mapping.get('price')
            if price_idx is not None and price_idx < len(row):
                try:
                    price_val = row.iloc[price_idx]
                    if price_val and str(price_val).lower() not in ['nan', 'none']:
                        price_str = str(price_val).replace(',', '').replace('$', '')
                        target_price = Decimal(price_str)
                except Exception:
                    pass

            # Get specifications
            specs = ""
            spec_idx = column_mapping.get('specifications')
            if spec_idx is not None and spec_idx < len(row):
                spec_val = row.iloc[spec_idx]
                if spec_val and str(spec_val).lower() not in ['nan', 'none']:
                    specs = str(spec_val).strip()

            return ParsedRFQItem(
                line_number=line_number,
                description=description.strip(),
                quantity=quantity,
                unit=unit,
                specifications=specs,
                target_price=target_price
            )

        except Exception as e:
            self.warnings.append(f"Error parsing row {line_number}: {str(e)}")
            return None

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string into date object."""
        date_formats = [
            '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d',
            '%d-%m-%Y', '%m-%d-%Y',
            '%d %B %Y', '%B %d, %Y',
            '%d/%m/%y', '%m/%d/%y'
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        return None

    def normalize_unit(self, unit_str: str) -> str:
        """Normalize unit string to standard code."""
        unit_lower = unit_str.lower().strip()

        for code, pattern in self.UNIT_PATTERNS.items():
            if re.match(pattern, unit_lower):
                return code

        return unit_str.upper()[:10] if unit_str else 'EA'

    def get_errors(self) -> List[str]:
        """Get list of parsing errors."""
        return self.errors

    def get_warnings(self) -> List[str]:
        """Get list of parsing warnings."""
        return self.warnings

    def clear_messages(self) -> None:
        """Clear errors and warnings."""
        self.errors = []
        self.warnings = []
