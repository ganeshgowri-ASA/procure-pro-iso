"""Vendor management database models."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

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


class VendorStatus(str, Enum):
    """Vendor status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"


class CertificationType(str, Enum):
    """ISO certification types."""

    ISO_9001 = "ISO 9001"
    ISO_14001 = "ISO 14001"
    ISO_17025 = "ISO 17025"
    ISO_45001 = "ISO 45001"
    IATF_16949 = "IATF 16949"
    ISO_22000 = "ISO 22000"
    ISO_27001 = "ISO 27001"
    OTHER = "Other"


class VendorCategory(Base):
    """Vendor category model for organizing vendors."""

    __tablename__ = "vendor_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("vendor_categories.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
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
    parent: Mapped[Optional["VendorCategory"]] = relationship(
        "VendorCategory",
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[List["VendorCategory"]] = relationship(
        "VendorCategory",
        back_populates="parent",
    )
    vendors: Mapped[List["Vendor"]] = relationship(
        "Vendor",
        back_populates="category",
    )


class Vendor(Base):
    """Vendor model for managing supplier information."""

    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Contact
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fax: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Category
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("vendor_categories.id"), nullable=True
    )

    # Status and metadata
    status: Mapped[str] = mapped_column(
        String(20), default=VendorStatus.PENDING.value
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Performance metrics
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    on_time_delivery_rate: Mapped[float] = mapped_column(Float, default=0.0)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    registered_at: Mapped[Optional[datetime]] = mapped_column(
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
    category: Mapped[Optional["VendorCategory"]] = relationship(
        "VendorCategory",
        back_populates="vendors",
    )
    certifications: Mapped[List["VendorCertification"]] = relationship(
        "VendorCertification",
        back_populates="vendor",
        cascade="all, delete-orphan",
    )
    contacts: Mapped[List["VendorContact"]] = relationship(
        "VendorContact",
        back_populates="vendor",
        cascade="all, delete-orphan",
    )
    ratings: Mapped[List["VendorRating"]] = relationship(
        "VendorRating",
        back_populates="vendor",
        cascade="all, delete-orphan",
    )
    rfq_invitations: Mapped[List["RFQVendorInvitation"]] = relationship(
        "RFQVendorInvitation",
        back_populates="vendor",
    )


class VendorCertification(Base):
    """Vendor certification tracking for ISO standards."""

    __tablename__ = "vendor_certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    certification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    certification_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    issuing_body: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    issue_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
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
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="certifications")

    __table_args__ = (
        UniqueConstraint(
            "vendor_id", "certification_type", name="uq_vendor_certification"
        ),
    )


class VendorContact(Base):
    """Vendor contact information."""

    __tablename__ = "vendor_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
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
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="contacts")


class VendorRating(Base):
    """Vendor performance rating and history."""

    __tablename__ = "vendor_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    rating_period: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "2024-Q1"

    # Rating categories (1-5 scale)
    quality_rating: Mapped[float] = mapped_column(Float, default=0.0)
    delivery_rating: Mapped[float] = mapped_column(Float, default=0.0)
    price_rating: Mapped[float] = mapped_column(Float, default=0.0)
    service_rating: Mapped[float] = mapped_column(Float, default=0.0)
    communication_rating: Mapped[float] = mapped_column(Float, default=0.0)
    overall_rating: Mapped[float] = mapped_column(Float, default=0.0)

    # Performance metrics
    orders_placed: Mapped[int] = mapped_column(Integer, default=0)
    orders_completed: Mapped[int] = mapped_column(Integer, default=0)
    orders_on_time: Mapped[int] = mapped_column(Integer, default=0)
    defect_count: Mapped[int] = mapped_column(Integer, default=0)
    total_value: Mapped[float] = mapped_column(Float, default=0.0)

    # Evaluation
    evaluated_by: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    evaluation_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("vendor_id", "rating_period", name="uq_vendor_rating_period"),
    )


# Forward reference for RFQVendorInvitation
from app.models.rfq import RFQVendorInvitation  # noqa: E402, F401
