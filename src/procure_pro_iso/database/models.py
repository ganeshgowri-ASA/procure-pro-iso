"""
SQLAlchemy database models for Procure-Pro-ISO.

These models mirror the Pydantic models but are designed for database storage.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class ParseResultDB(Base, TimestampMixin):
    """
    Record of a parsing operation.

    Stores metadata about each parse attempt for audit and debugging.
    """

    __tablename__ = "parse_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_file = Column(String(512), nullable=False)
    source_type = Column(String(50), nullable=False)  # excel, pdf, csv
    success = Column(Boolean, nullable=False, default=False)
    error_message = Column(Text, nullable=True)
    raw_data = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    # Relationship to RFQ document
    rfq_document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rfq_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    rfq_document = relationship("RFQDocumentDB", back_populates="parse_results")

    __table_args__ = (
        Index("ix_parse_results_source_file", "source_file"),
        Index("ix_parse_results_created_at", "created_at"),
    )


class RFQDocumentDB(Base, TimestampMixin):
    """
    RFQ document database model.

    Represents a complete RFQ with all associated vendor quotes.
    """

    __tablename__ = "rfq_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    rfq_number = Column(String(100), nullable=True, index=True)
    rfq_title = Column(String(500), nullable=True)
    project_name = Column(String(200), nullable=True)
    issue_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    buyer_name = Column(String(200), nullable=True)
    buyer_organization = Column(String(200), nullable=True)
    status = Column(String(50), nullable=False, default="active")
    notes = Column(Text, nullable=True)

    # Relationships
    vendor_quotes = relationship(
        "VendorQuoteDB",
        back_populates="rfq_document",
        cascade="all, delete-orphan",
    )
    parse_results = relationship(
        "ParseResultDB",
        back_populates="rfq_document",
    )

    __table_args__ = (
        Index("ix_rfq_documents_status", "status"),
        UniqueConstraint("rfq_number", name="uq_rfq_number"),
    )


class VendorQuoteDB(Base, TimestampMixin):
    """
    Vendor quote database model.

    Represents a quote from a specific vendor for an RFQ.
    """

    __tablename__ = "vendor_quotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    rfq_document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rfq_documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    vendor_name = Column(String(200), nullable=False, index=True)
    vendor_code = Column(String(50), nullable=True)
    contact_person = Column(String(200), nullable=True)
    contact_email = Column(String(254), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    quote_reference = Column(String(100), nullable=True)
    quote_date = Column(Date, nullable=True)
    validity_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="received")
    payment_terms = Column(String(200), nullable=True)
    total_amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(10), nullable=False, default="USD")
    country_of_origin = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    rfq_document = relationship("RFQDocumentDB", back_populates="vendor_quotes")
    items = relationship(
        "EquipmentItemDB",
        back_populates="vendor_quote",
        cascade="all, delete-orphan",
    )
    delivery_terms = relationship(
        "DeliveryTermsDB",
        back_populates="vendor_quote",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_vendor_quotes_vendor_name", "vendor_name"),
        Index("ix_vendor_quotes_status", "status"),
    )


class EquipmentItemDB(Base, TimestampMixin):
    """
    Equipment item database model.

    Represents a single item in a vendor quote.
    """

    __tablename__ = "equipment_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_quote_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vendor_quotes.id", ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    model_number = Column(String(100), nullable=True)
    manufacturer = Column(String(200), nullable=True)
    country_of_origin = Column(String(100), nullable=True)
    warranty_period = Column(String(100), nullable=True)
    certifications = Column(JSON, nullable=True)  # List of certification strings

    # Relationships
    vendor_quote = relationship("VendorQuoteDB", back_populates="items")
    pricing = relationship(
        "PriceBreakdownDB",
        back_populates="equipment_item",
        uselist=False,
        cascade="all, delete-orphan",
    )
    technical_specs = relationship(
        "TechnicalSpecDB",
        back_populates="equipment_item",
        cascade="all, delete-orphan",
    )
    delivery_terms = relationship(
        "DeliveryTermsDB",
        back_populates="equipment_item",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_equipment_items_name", "name"),
        Index("ix_equipment_items_model_number", "model_number"),
    )


class PriceBreakdownDB(Base, TimestampMixin):
    """
    Price breakdown database model.

    Stores detailed pricing information for an equipment item.
    """

    __tablename__ = "price_breakdowns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    equipment_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipment_items.id", ondelete="CASCADE"),
        nullable=False,
    )

    unit_price = Column(Numeric(15, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    currency = Column(String(10), nullable=False, default="USD")
    total_price = Column(Numeric(15, 2), nullable=True)
    discount_percent = Column(Numeric(5, 2), nullable=True)
    tax_percent = Column(Numeric(5, 2), nullable=True)
    shipping_cost = Column(Numeric(15, 2), nullable=True)
    installation_cost = Column(Numeric(15, 2), nullable=True)
    warranty_cost = Column(Numeric(15, 2), nullable=True)
    grand_total = Column(Numeric(15, 2), nullable=True)

    # Relationship
    equipment_item = relationship("EquipmentItemDB", back_populates="pricing")


class TechnicalSpecDB(Base, TimestampMixin):
    """
    Technical specification database model.

    Stores individual technical specifications for equipment items.
    """

    __tablename__ = "technical_specs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    equipment_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipment_items.id", ondelete="CASCADE"),
        nullable=False,
    )

    parameter = Column(String(200), nullable=False)
    value = Column(String(500), nullable=False)
    unit = Column(String(50), nullable=True)
    is_compliant = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationship
    equipment_item = relationship("EquipmentItemDB", back_populates="technical_specs")

    __table_args__ = (
        Index("ix_technical_specs_parameter", "parameter"),
    )


class DeliveryTermsDB(Base, TimestampMixin):
    """
    Delivery terms database model.

    Stores delivery information for vendor quotes or equipment items.
    """

    __tablename__ = "delivery_terms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Can be associated with either vendor quote or equipment item
    vendor_quote_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vendor_quotes.id", ondelete="CASCADE"),
        nullable=True,
    )
    equipment_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("equipment_items.id", ondelete="CASCADE"),
        nullable=True,
    )

    incoterm = Column(String(10), nullable=True)
    delivery_time_days = Column(Integer, nullable=True)
    delivery_time_text = Column(String(200), nullable=True)
    delivery_location = Column(String(300), nullable=True)
    shipping_method = Column(String(100), nullable=True)
    partial_shipment_allowed = Column(Boolean, nullable=True)

    # Relationships
    vendor_quote = relationship("VendorQuoteDB", back_populates="delivery_terms")
    equipment_item = relationship("EquipmentItemDB", back_populates="delivery_terms")

    __table_args__ = (
        Index("ix_delivery_terms_incoterm", "incoterm"),
    )
