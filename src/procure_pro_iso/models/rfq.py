"""
RFQ (Request for Quote) data models for Procure-Pro-ISO.

These models define the structure for parsed RFQ documents, vendor quotes,
technical specifications, and pricing information.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class Currency(str, Enum):
    """Supported currencies for pricing."""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    INR = "INR"
    CNY = "CNY"
    AED = "AED"
    OTHER = "OTHER"


class QuoteStatus(str, Enum):
    """Status of a vendor quote."""

    RECEIVED = "received"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class DeliveryTerms(BaseModel):
    """Delivery terms and conditions from vendor quote."""

    incoterm: str | None = Field(
        default=None,
        description="Incoterm (e.g., FOB, CIF, DDP, EXW)",
    )
    delivery_time_days: int | None = Field(
        default=None,
        ge=0,
        description="Delivery time in days",
    )
    delivery_time_text: str | None = Field(
        default=None,
        description="Original delivery time text from document",
    )
    delivery_location: str | None = Field(
        default=None,
        description="Delivery destination",
    )
    shipping_method: str | None = Field(
        default=None,
        description="Shipping method (air, sea, land)",
    )
    partial_shipment_allowed: bool | None = Field(
        default=None,
        description="Whether partial shipments are allowed",
    )

    @field_validator("incoterm")
    @classmethod
    def normalize_incoterm(cls, v: str | None) -> str | None:
        """Normalize incoterm to uppercase."""
        if v is None:
            return None
        return v.upper().strip()


class TechnicalSpecification(BaseModel):
    """Technical specification for an equipment item."""

    parameter: str = Field(
        ...,
        min_length=1,
        description="Specification parameter name",
    )
    value: str = Field(
        ...,
        description="Specification value",
    )
    unit: str | None = Field(
        default=None,
        description="Unit of measurement",
    )
    is_compliant: bool | None = Field(
        default=None,
        description="Whether spec meets requirements",
    )
    notes: str | None = Field(
        default=None,
        description="Additional notes",
    )


class PriceBreakdown(BaseModel):
    """Detailed price breakdown for a quoted item."""

    unit_price: Decimal = Field(
        ...,
        ge=0,
        description="Price per unit",
    )
    quantity: int = Field(
        default=1,
        ge=1,
        description="Quantity quoted",
    )
    currency: Currency = Field(
        default=Currency.USD,
        description="Currency code",
    )
    total_price: Decimal | None = Field(
        default=None,
        ge=0,
        description="Total price (unit_price * quantity)",
    )
    discount_percent: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Discount percentage",
    )
    tax_percent: Decimal | None = Field(
        default=None,
        ge=0,
        description="Tax percentage",
    )
    shipping_cost: Decimal | None = Field(
        default=None,
        ge=0,
        description="Shipping/freight cost",
    )
    installation_cost: Decimal | None = Field(
        default=None,
        ge=0,
        description="Installation cost",
    )
    warranty_cost: Decimal | None = Field(
        default=None,
        ge=0,
        description="Extended warranty cost",
    )
    grand_total: Decimal | None = Field(
        default=None,
        ge=0,
        description="Grand total including all costs",
    )

    @model_validator(mode="after")
    def calculate_totals(self) -> "PriceBreakdown":
        """Calculate total price if not provided."""
        if self.total_price is None:
            self.total_price = self.unit_price * self.quantity
        return self

    @field_validator("unit_price", "total_price", "shipping_cost", "installation_cost",
                     "warranty_cost", "grand_total", mode="before")
    @classmethod
    def parse_decimal(cls, v: Any) -> Decimal | None:
        """Parse various formats to Decimal."""
        if v is None:
            return None
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            # Remove currency symbols and commas
            cleaned = v.replace("$", "").replace("€", "").replace("£", "")
            cleaned = cleaned.replace(",", "").replace(" ", "").strip()
            if cleaned:
                return Decimal(cleaned)
        return None


class EquipmentItem(BaseModel):
    """An equipment item in a vendor quote."""

    name: str = Field(
        ...,
        min_length=1,
        description="Equipment/item name",
    )
    description: str | None = Field(
        default=None,
        description="Detailed description",
    )
    model_number: str | None = Field(
        default=None,
        description="Model number/SKU",
    )
    manufacturer: str | None = Field(
        default=None,
        description="Manufacturer name",
    )
    country_of_origin: str | None = Field(
        default=None,
        description="Country of origin/manufacture",
    )
    pricing: PriceBreakdown | None = Field(
        default=None,
        description="Pricing information",
    )
    technical_specs: list[TechnicalSpecification] = Field(
        default_factory=list,
        description="Technical specifications",
    )
    delivery: DeliveryTerms | None = Field(
        default=None,
        description="Delivery terms for this item",
    )
    warranty_period: str | None = Field(
        default=None,
        description="Warranty period",
    )
    certifications: list[str] = Field(
        default_factory=list,
        description="Relevant certifications (ISO, CE, etc.)",
    )


class VendorQuote(BaseModel):
    """A vendor's quote for an RFQ."""

    vendor_name: str = Field(
        ...,
        min_length=1,
        description="Vendor/supplier name",
    )
    vendor_code: str | None = Field(
        default=None,
        description="Internal vendor code",
    )
    contact_person: str | None = Field(
        default=None,
        description="Contact person name",
    )
    contact_email: str | None = Field(
        default=None,
        description="Contact email",
    )
    contact_phone: str | None = Field(
        default=None,
        description="Contact phone",
    )
    quote_reference: str | None = Field(
        default=None,
        description="Vendor's quote reference number",
    )
    quote_date: date | None = Field(
        default=None,
        description="Date of quote",
    )
    validity_date: date | None = Field(
        default=None,
        description="Quote validity/expiry date",
    )
    status: QuoteStatus = Field(
        default=QuoteStatus.RECEIVED,
        description="Quote status",
    )
    items: list[EquipmentItem] = Field(
        default_factory=list,
        description="Quoted items",
    )
    delivery: DeliveryTerms | None = Field(
        default=None,
        description="General delivery terms",
    )
    payment_terms: str | None = Field(
        default=None,
        description="Payment terms",
    )
    total_amount: Decimal | None = Field(
        default=None,
        ge=0,
        description="Total quote amount",
    )
    currency: Currency = Field(
        default=Currency.USD,
        description="Quote currency",
    )
    notes: str | None = Field(
        default=None,
        description="Additional notes/comments",
    )
    country_of_origin: str | None = Field(
        default=None,
        description="Default country of origin for items",
    )

    @field_validator("quote_date", "validity_date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> date | None:
        """Parse various date formats."""
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            # Try common date formats
            formats = [
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%Y/%m/%d",
                "%d.%m.%Y",
                "%B %d, %Y",
                "%b %d, %Y",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(v.strip(), fmt).date()
                except ValueError:
                    continue
        return None


class RFQDocument(BaseModel):
    """A complete RFQ document with all vendor quotes."""

    rfq_number: str | None = Field(
        default=None,
        description="RFQ reference number",
    )
    rfq_title: str | None = Field(
        default=None,
        description="RFQ title/description",
    )
    project_name: str | None = Field(
        default=None,
        description="Associated project name",
    )
    issue_date: date | None = Field(
        default=None,
        description="RFQ issue date",
    )
    due_date: date | None = Field(
        default=None,
        description="RFQ response due date",
    )
    buyer_name: str | None = Field(
        default=None,
        description="Buyer/purchaser name",
    )
    buyer_organization: str | None = Field(
        default=None,
        description="Buyer organization",
    )
    vendor_quotes: list[VendorQuote] = Field(
        default_factory=list,
        description="List of vendor quotes",
    )

    @field_validator("issue_date", "due_date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> date | None:
        """Parse various date formats."""
        return VendorQuote.parse_date(v)


class ValidationError(BaseModel):
    """Represents a validation error during parsing."""

    field: str = Field(
        ...,
        description="Field path that failed validation",
    )
    message: str = Field(
        ...,
        description="Error message",
    )
    value: Any = Field(
        default=None,
        description="The invalid value",
    )
    row: int | None = Field(
        default=None,
        description="Row number in source document",
    )


class ParsingError(BaseModel):
    """Represents an error during document parsing."""

    error_type: str = Field(
        ...,
        description="Type of error",
    )
    message: str = Field(
        ...,
        description="Error message",
    )
    location: str | None = Field(
        default=None,
        description="Location in document where error occurred",
    )


class ParsedRFQResult(BaseModel):
    """Result of parsing an RFQ document."""

    success: bool = Field(
        ...,
        description="Whether parsing was successful",
    )
    document: RFQDocument | None = Field(
        default=None,
        description="Parsed RFQ document",
    )
    source_file: str = Field(
        ...,
        description="Source file path",
    )
    source_type: str = Field(
        ...,
        description="Source file type (excel, pdf, csv)",
    )
    parsing_errors: list[ParsingError] = Field(
        default_factory=list,
        description="Errors encountered during parsing",
    )
    validation_errors: list[ValidationError] = Field(
        default_factory=list,
        description="Validation errors",
    )
    raw_data: dict[str, Any] | None = Field(
        default=None,
        description="Raw extracted data before validation",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    def to_json(self, indent: int = 2) -> str:
        """Export result to JSON string."""
        return self.model_dump_json(indent=indent)

    def to_dict(self) -> dict[str, Any]:
        """Export result to dictionary."""
        return self.model_dump()
