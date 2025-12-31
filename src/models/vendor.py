"""Vendor data models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Text, Float
from sqlalchemy.dialects.sqlite import JSON

from src.config.database import Base


class VendorStatus(str, Enum):
    """Vendor status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    BLACKLISTED = "blacklisted"
    SUSPENDED = "suspended"


class VendorDB(Base):
    """SQLAlchemy model for vendors."""

    __tablename__ = "vendors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    status = Column(SQLEnum(VendorStatus), default=VendorStatus.PENDING)
    certifications = Column(JSON, default=list)
    iso_standards = Column(JSON, default=list)
    quality_rating = Column(Float, default=0.0)
    delivery_rating = Column(Float, default=0.0)
    price_competitiveness = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)


class VendorBase(BaseModel):
    """Base vendor model."""

    name: str = Field(..., min_length=1, max_length=255, description="Vendor company name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique vendor code")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    address: Optional[str] = Field(None, description="Business address")
    country: Optional[str] = Field(None, description="Country of operation")
    industry: Optional[str] = Field(None, description="Industry sector")
    certifications: list[str] = Field(default_factory=list, description="Certifications held")
    iso_standards: list[str] = Field(
        default_factory=list, description="ISO standards compliance"
    )


class VendorCreate(VendorBase):
    """Model for creating a new vendor."""

    status: VendorStatus = VendorStatus.PENDING
    quality_rating: float = Field(0.0, ge=0, le=100)
    delivery_rating: float = Field(0.0, ge=0, le=100)
    price_competitiveness: float = Field(0.0, ge=0, le=100)


class VendorUpdate(BaseModel):
    """Model for updating a vendor."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[VendorStatus] = None
    certifications: Optional[list[str]] = None
    iso_standards: Optional[list[str]] = None
    quality_rating: Optional[float] = Field(None, ge=0, le=100)
    delivery_rating: Optional[float] = Field(None, ge=0, le=100)
    price_competitiveness: Optional[float] = Field(None, ge=0, le=100)


class Vendor(VendorBase):
    """Complete vendor model with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    status: VendorStatus = VendorStatus.PENDING
    quality_rating: float = Field(0.0, ge=0, le=100)
    delivery_rating: float = Field(0.0, ge=0, le=100)
    price_competitiveness: float = Field(0.0, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VendorResponse(Vendor):
    """Vendor response model for API."""

    model_config = ConfigDict(from_attributes=True)
