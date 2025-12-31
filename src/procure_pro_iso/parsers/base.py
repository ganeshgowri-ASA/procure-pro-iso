"""
Base parser class for RFQ document parsing.

Provides common functionality and interface for all document parsers.
"""

import re
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from procure_pro_iso.models.rfq import (
    Currency,
    DeliveryTerms,
    EquipmentItem,
    ParsedRFQResult,
    ParsingError,
    PriceBreakdown,
    RFQDocument,
    TechnicalSpecification,
    ValidationError,
    VendorQuote,
)


class FieldPatterns:
    """Regex patterns for extracting key fields from text."""

    # Equipment/item name patterns
    EQUIPMENT_NAME = [
        r"(?:equipment|item|product|model)[\s:]+(.+?)(?:\n|$)",
        r"(?:description)[\s:]+(.+?)(?:\n|$)",
    ]

    # Vendor patterns
    VENDOR_NAME = [
        r"(?:vendor|supplier|company|from)[\s:]+(.+?)(?:\n|$)",
        r"(?:quotation\s+from|quote\s+from)[\s:]+(.+?)(?:\n|$)",
    ]

    # Price patterns
    PRICE = [
        r"(?:price|cost|amount|total)[\s:]*[\$€£¥₹]?\s*([\d,]+\.?\d*)",
        r"[\$€£¥₹]\s*([\d,]+\.?\d*)",
        r"([\d,]+\.?\d*)\s*(?:USD|EUR|GBP|JPY|INR|CNY|AED)",
    ]

    # Delivery time patterns
    DELIVERY_TIME = [
        r"(?:delivery|lead\s*time|shipping)[\s:]*(\d+)\s*(?:days?|weeks?|months?)",
        r"(\d+)\s*(?:days?|weeks?|months?)\s*(?:delivery|lead\s*time)",
        r"(?:within|in)\s*(\d+)\s*(?:days?|weeks?|months?)",
    ]

    # Country of origin patterns
    COUNTRY_OF_ORIGIN = [
        r"(?:country\s*of\s*origin|made\s*in|manufactured\s*in|origin)[\s:]+([A-Za-z\s]+?)(?:\n|$|,)",
        r"(?:COO|C\.O\.O\.)[\s:]+([A-Za-z\s]+?)(?:\n|$|,)",
    ]

    # Currency patterns
    CURRENCY = [
        r"[\$]",  # USD
        r"[€]",  # EUR
        r"[£]",  # GBP
        r"[¥]",  # JPY/CNY
        r"[₹]",  # INR
        r"\b(USD|EUR|GBP|JPY|INR|CNY|AED)\b",
    ]

    # Incoterm patterns
    INCOTERMS = [
        r"\b(EXW|FCA|CPT|CIP|DAP|DPU|DDP|FAS|FOB|CFR|CIF)\b",
    ]

    # Technical specification patterns
    TECH_SPEC = [
        r"([A-Za-z\s]+)[\s:]+(\d+\.?\d*)\s*([A-Za-z%°]+)?",
    ]


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    SUPPORTED_EXTENSIONS: list[str] = []

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the parser.

        Args:
            strict_mode: If True, raise exceptions on validation errors.
                        If False, collect errors and continue parsing.
        """
        self.strict_mode = strict_mode
        self.errors: list[ParsingError] = []
        self.validation_errors: list[ValidationError] = []

    @abstractmethod
    def parse(self, file_path: str | Path) -> ParsedRFQResult:
        """
        Parse a document and extract RFQ data.

        Args:
            file_path: Path to the document file.

        Returns:
            ParsedRFQResult containing the extracted data.
        """
        pass

    @abstractmethod
    def _extract_raw_data(self, file_path: Path) -> dict[str, Any]:
        """
        Extract raw data from the document.

        Args:
            file_path: Path to the document file.

        Returns:
            Dictionary containing raw extracted data.
        """
        pass

    def can_parse(self, file_path: str | Path) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            file_path: Path to the file.

        Returns:
            True if the parser can handle this file type.
        """
        path = Path(file_path)
        return path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def _add_error(self, error_type: str, message: str, location: str | None = None) -> None:
        """Add a parsing error to the error list."""
        self.errors.append(
            ParsingError(error_type=error_type, message=message, location=location)
        )

    def _add_validation_error(
        self, field: str, message: str, value: Any = None, row: int | None = None
    ) -> None:
        """Add a validation error to the error list."""
        self.validation_errors.append(
            ValidationError(field=field, message=message, value=value, row=row)
        )

    def _extract_price(self, text: str) -> tuple[Decimal | None, Currency]:
        """
        Extract price and currency from text.

        Args:
            text: Text containing price information.

        Returns:
            Tuple of (price as Decimal, Currency enum).
        """
        if not text:
            return None, Currency.USD

        # Determine currency
        currency = Currency.USD
        if "€" in text or "EUR" in text.upper():
            currency = Currency.EUR
        elif "£" in text or "GBP" in text.upper():
            currency = Currency.GBP
        elif "¥" in text or "JPY" in text.upper():
            currency = Currency.JPY
        elif "₹" in text or "INR" in text.upper():
            currency = Currency.INR
        elif "CNY" in text.upper() or "RMB" in text.upper():
            currency = Currency.CNY
        elif "AED" in text.upper():
            currency = Currency.AED

        # Extract numeric value
        for pattern in FieldPatterns.PRICE:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(",", "")
                    return Decimal(price_str), currency
                except (InvalidOperation, IndexError):
                    continue

        # Try to find any number
        numbers = re.findall(r"[\d,]+\.?\d*", text)
        if numbers:
            try:
                price_str = numbers[0].replace(",", "")
                return Decimal(price_str), currency
            except InvalidOperation:
                pass

        return None, currency

    def _extract_delivery_days(self, text: str) -> int | None:
        """
        Extract delivery time in days from text.

        Args:
            text: Text containing delivery information.

        Returns:
            Delivery time in days, or None if not found.
        """
        if not text:
            return None

        for pattern in FieldPatterns.DELIVERY_TIME:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = int(match.group(1))
                    # Check unit and convert to days
                    if "week" in text.lower():
                        return value * 7
                    elif "month" in text.lower():
                        return value * 30
                    return value
                except (ValueError, IndexError):
                    continue

        return None

    def _extract_country_of_origin(self, text: str) -> str | None:
        """
        Extract country of origin from text.

        Args:
            text: Text containing country information.

        Returns:
            Country name, or None if not found.
        """
        if not text:
            return None

        for pattern in FieldPatterns.COUNTRY_OF_ORIGIN:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                country = match.group(1).strip()
                # Clean up common artifacts
                country = re.sub(r"[,;:\.]$", "", country)
                if len(country) > 2:  # Avoid matching abbreviations
                    return country.title()

        return None

    def _extract_incoterm(self, text: str) -> str | None:
        """
        Extract incoterm from text.

        Args:
            text: Text containing delivery terms.

        Returns:
            Incoterm code, or None if not found.
        """
        if not text:
            return None

        for pattern in FieldPatterns.INCOTERMS:
            match = re.search(pattern, text.upper())
            if match:
                return match.group(1)

        return None

    def _normalize_column_name(self, name: str) -> str:
        """
        Normalize a column name for matching.

        Args:
            name: Original column name.

        Returns:
            Normalized lowercase name with special chars removed.
        """
        if not name:
            return ""
        # Convert to lowercase and remove special characters
        normalized = re.sub(r"[^a-z0-9]", "", str(name).lower())
        return normalized

    def _map_column_to_field(self, column_name: str) -> str | None:
        """
        Map a column name to a standard field name.

        Args:
            column_name: Original column name from document.

        Returns:
            Standard field name, or None if no mapping found.
        """
        normalized = self._normalize_column_name(column_name)

        # Equipment/Item name mappings
        if any(
            x in normalized
            for x in ["equipment", "item", "product", "description", "name", "material"]
        ):
            if "vendor" not in normalized and "supplier" not in normalized:
                return "equipment_name"

        # Vendor mappings
        if any(x in normalized for x in ["vendor", "supplier", "company", "manufacturer"]):
            return "vendor_name"

        # Price mappings
        if any(x in normalized for x in ["price", "cost", "amount", "rate", "value"]):
            if "unit" in normalized:
                return "unit_price"
            elif "total" in normalized:
                return "total_price"
            return "unit_price"

        # Quantity mappings
        if any(x in normalized for x in ["quantity", "qty", "units", "nos"]):
            return "quantity"

        # Delivery mappings
        if any(x in normalized for x in ["delivery", "leadtime", "lead"]):
            return "delivery_time"

        # Country of origin mappings
        if any(x in normalized for x in ["country", "origin", "coo", "madein"]):
            return "country_of_origin"

        # Model/Part number mappings
        if any(x in normalized for x in ["model", "part", "sku", "partnumber", "modelnumber"]):
            return "model_number"

        # Currency mappings
        if "currency" in normalized:
            return "currency"

        # Specification mappings
        if any(x in normalized for x in ["spec", "specification", "technical"]):
            return "technical_specs"

        # Warranty mappings
        if "warranty" in normalized:
            return "warranty"

        return None

    def _build_equipment_item(
        self,
        name: str,
        row_data: dict[str, Any],
    ) -> EquipmentItem:
        """
        Build an EquipmentItem from extracted data.

        Args:
            name: Equipment/item name.
            row_data: Dictionary of extracted field values.

        Returns:
            EquipmentItem instance.
        """
        # Extract pricing
        unit_price = row_data.get("unit_price")
        quantity = row_data.get("quantity", 1)
        currency_str = row_data.get("currency", "USD")

        pricing = None
        if unit_price is not None:
            try:
                if isinstance(unit_price, str):
                    price_val, currency = self._extract_price(unit_price)
                else:
                    price_val = Decimal(str(unit_price))
                    currency = Currency(currency_str) if currency_str else Currency.USD

                if price_val is not None:
                    pricing = PriceBreakdown(
                        unit_price=price_val,
                        quantity=int(quantity) if quantity else 1,
                        currency=currency,
                        total_price=row_data.get("total_price"),
                    )
            except (InvalidOperation, ValueError):
                pass

        # Extract delivery terms
        delivery = None
        delivery_text = row_data.get("delivery_time")
        if delivery_text:
            delivery_days = self._extract_delivery_days(str(delivery_text))
            incoterm = self._extract_incoterm(str(row_data.get("incoterm", "")))
            delivery = DeliveryTerms(
                delivery_time_days=delivery_days,
                delivery_time_text=str(delivery_text),
                incoterm=incoterm,
            )

        # Extract technical specs
        tech_specs = []
        specs_data = row_data.get("technical_specs")
        if specs_data:
            if isinstance(specs_data, dict):
                for param, value in specs_data.items():
                    tech_specs.append(
                        TechnicalSpecification(parameter=str(param), value=str(value))
                    )
            elif isinstance(specs_data, str):
                # Try to parse "param: value" format
                for line in specs_data.split("\n"):
                    if ":" in line:
                        param, value = line.split(":", 1)
                        tech_specs.append(
                            TechnicalSpecification(
                                parameter=param.strip(), value=value.strip()
                            )
                        )

        return EquipmentItem(
            name=name,
            description=row_data.get("description"),
            model_number=row_data.get("model_number"),
            manufacturer=row_data.get("manufacturer"),
            country_of_origin=row_data.get("country_of_origin"),
            pricing=pricing,
            technical_specs=tech_specs,
            delivery=delivery,
            warranty_period=row_data.get("warranty"),
        )

    def _build_vendor_quote(
        self,
        vendor_name: str,
        items: list[EquipmentItem],
        metadata: dict[str, Any] | None = None,
    ) -> VendorQuote:
        """
        Build a VendorQuote from vendor data and items.

        Args:
            vendor_name: Name of the vendor.
            items: List of equipment items.
            metadata: Additional vendor metadata.

        Returns:
            VendorQuote instance.
        """
        metadata = metadata or {}

        # Calculate total amount
        total = Decimal("0")
        currency = Currency.USD
        for item in items:
            if item.pricing and item.pricing.total_price:
                total += item.pricing.total_price
                currency = item.pricing.currency

        # Determine common country of origin
        countries = [item.country_of_origin for item in items if item.country_of_origin]
        common_country = countries[0] if countries else None

        return VendorQuote(
            vendor_name=vendor_name,
            vendor_code=metadata.get("vendor_code"),
            contact_person=metadata.get("contact_person"),
            contact_email=metadata.get("contact_email"),
            quote_reference=metadata.get("quote_reference"),
            quote_date=metadata.get("quote_date"),
            validity_date=metadata.get("validity_date"),
            items=items,
            total_amount=total if total > 0 else None,
            currency=currency,
            payment_terms=metadata.get("payment_terms"),
            country_of_origin=common_country,
            notes=metadata.get("notes"),
        )

    def _create_result(
        self,
        file_path: Path,
        source_type: str,
        document: RFQDocument | None = None,
        raw_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ParsedRFQResult:
        """
        Create a ParsedRFQResult with current errors and data.

        Args:
            file_path: Source file path.
            source_type: Type of source file.
            document: Parsed RFQ document, if successful.
            raw_data: Raw extracted data.
            metadata: Additional metadata.

        Returns:
            ParsedRFQResult instance.
        """
        success = document is not None and len(self.errors) == 0
        if self.strict_mode and self.validation_errors:
            success = False

        return ParsedRFQResult(
            success=success,
            document=document,
            source_file=str(file_path),
            source_type=source_type,
            parsing_errors=self.errors.copy(),
            validation_errors=self.validation_errors.copy(),
            raw_data=raw_data,
            metadata=metadata or {},
        )
