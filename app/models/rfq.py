"""RFQ (Request for Quotation) workflow database models."""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class RFQStatus(str, Enum):
    """RFQ status workflow enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    UNDER_REVIEW = "under_review"
    AWARDED = "awarded"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class InvitationStatus(str, Enum):
    """Vendor invitation status enumeration."""

    PENDING = "pending"
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class QuotationStatus(str, Enum):
    """Quotation status enumeration."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_EVALUATION = "under_evaluation"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class RFQ(Base):
    """Request for Quotation model."""

    __tablename__ = "rfqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rfq_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default=RFQStatus.DRAFT.value)

    # Dates
    issue_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    submission_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    validity_period_days: Mapped[int] = mapped_column(Integer, default=30)

    # Requirements
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_terms: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    warranty_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technical_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    compliance_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Budget
    budget_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")

    # Metadata
    created_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    project_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    items: Mapped[List["RFQItem"]] = relationship(
        "RFQItem",
        back_populates="rfq",
        cascade="all, delete-orphan",
    )
    vendor_invitations: Mapped[List["RFQVendorInvitation"]] = relationship(
        "RFQVendorInvitation",
        back_populates="rfq",
        cascade="all, delete-orphan",
    )
    quotations: Mapped[List["Quotation"]] = relationship(
        "Quotation",
        back_populates="rfq",
        cascade="all, delete-orphan",
    )

    # Status workflow transitions
    VALID_TRANSITIONS = {
        RFQStatus.DRAFT: [RFQStatus.PUBLISHED, RFQStatus.CANCELLED],
        RFQStatus.PUBLISHED: [RFQStatus.UNDER_REVIEW, RFQStatus.CANCELLED],
        RFQStatus.UNDER_REVIEW: [RFQStatus.AWARDED, RFQStatus.PUBLISHED, RFQStatus.CANCELLED],
        RFQStatus.AWARDED: [RFQStatus.CLOSED],
        RFQStatus.CLOSED: [],
        RFQStatus.CANCELLED: [],
    }

    def can_transition_to(self, new_status: RFQStatus) -> bool:
        """Check if transition to new status is valid."""
        current = RFQStatus(self.status)
        return new_status in self.VALID_TRANSITIONS.get(current, [])


class RFQItem(Base):
    """RFQ line item for equipment specifications."""

    __tablename__ = "rfq_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rfq_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False
    )
    item_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Item details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)

    # Specifications
    specifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    brand_preference: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    model_preference: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    part_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Requirements
    required_delivery_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    alternative_allowed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Budget
    estimated_unit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    budget_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="items")
    quotation_items: Mapped[List["QuotationItem"]] = relationship(
        "QuotationItem",
        back_populates="rfq_item",
    )

    __table_args__ = (
        UniqueConstraint("rfq_id", "item_number", name="uq_rfq_item_number"),
    )


class RFQVendorInvitation(Base):
    """Vendor invitation to participate in RFQ."""

    __tablename__ = "rfq_vendor_invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rfq_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False
    )
    vendor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20), default=InvitationStatus.PENDING.value
    )
    invitation_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timestamps
    invited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    viewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Response
    decline_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="vendor_invitations")
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="rfq_invitations")

    __table_args__ = (
        UniqueConstraint("rfq_id", "vendor_id", name="uq_rfq_vendor_invitation"),
    )


class Quotation(Base):
    """Vendor quotation submission for RFQ."""

    __tablename__ = "quotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rfq_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False
    )
    vendor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    quotation_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), default=QuotationStatus.DRAFT.value
    )

    # Pricing
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    discount_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    tax_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0)
    shipping_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")

    # Terms
    validity_days: Mapped[int] = mapped_column(Integer, default=30)
    delivery_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    warranty_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Documents
    document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Evaluation
    technical_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    commercial_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evaluation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluated_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Timestamps
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="quotations")
    vendor: Mapped["Vendor"] = relationship("Vendor")
    items: Mapped[List["QuotationItem"]] = relationship(
        "QuotationItem",
        back_populates="quotation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("rfq_id", "vendor_id", name="uq_quotation_rfq_vendor"),
    )


class QuotationItem(Base):
    """Quotation line item with pricing."""

    __tablename__ = "quotation_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quotation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False
    )
    rfq_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rfq_items.id", ondelete="CASCADE"), nullable=False
    )

    # Pricing
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    # Offered product
    offered_brand: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    offered_model: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    offered_part_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_alternative: Mapped[bool] = mapped_column(Boolean, default=False)

    # Delivery
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    availability: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Notes
    specifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="items")
    rfq_item: Mapped["RFQItem"] = relationship("RFQItem", back_populates="quotation_items")

    __table_args__ = (
        UniqueConstraint(
            "quotation_id", "rfq_item_id", name="uq_quotation_item_rfq_item"
        ),
    )
