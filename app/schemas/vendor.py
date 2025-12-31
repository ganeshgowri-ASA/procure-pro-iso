"""Pydantic schemas for Vendor Management API."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.core.pagination import FilterParams
from app.models.vendor import CertificationType, VendorStatus


# Vendor Category Schemas
class VendorCategoryBase(BaseModel):
    """Base schema for vendor category."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True


class VendorCategoryCreate(VendorCategoryBase):
    """Schema for creating a vendor category."""

    pass


class VendorCategoryUpdate(BaseModel):
    """Schema for updating a vendor category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None


class VendorCategoryResponse(VendorCategoryBase):
    """Schema for vendor category response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Vendor Certification Schemas
class VendorCertificationBase(BaseModel):
    """Base schema for vendor certification."""

    certification_type: CertificationType
    certification_number: Optional[str] = Field(None, max_length=100)
    issuing_body: Optional[str] = Field(None, max_length=200)
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    document_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class VendorCertificationCreate(VendorCertificationBase):
    """Schema for creating a vendor certification."""

    pass


class VendorCertificationUpdate(BaseModel):
    """Schema for updating a vendor certification."""

    certification_type: Optional[CertificationType] = None
    certification_number: Optional[str] = Field(None, max_length=100)
    issuing_body: Optional[str] = Field(None, max_length=200)
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_verified: Optional[bool] = None
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = Field(None, max_length=200)
    document_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class VendorCertificationResponse(BaseModel):
    """Schema for vendor certification response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int
    certification_type: str
    certification_number: Optional[str] = None
    issuing_body: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_verified: bool
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = None
    document_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Vendor Contact Schemas
class VendorContactBase(BaseModel):
    """Base schema for vendor contact."""

    name: str = Field(..., min_length=1, max_length=200)
    title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    is_primary: bool = False
    is_active: bool = True
    notes: Optional[str] = None


class VendorContactCreate(VendorContactBase):
    """Schema for creating a vendor contact."""

    pass


class VendorContactUpdate(BaseModel):
    """Schema for updating a vendor contact."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    mobile: Optional[str] = Field(None, max_length=50)
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class VendorContactResponse(VendorContactBase):
    """Schema for vendor contact response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int
    created_at: datetime
    updated_at: datetime


# Vendor Rating Schemas
class VendorRatingBase(BaseModel):
    """Base schema for vendor rating."""

    rating_period: str = Field(..., min_length=1, max_length=20)
    quality_rating: float = Field(0.0, ge=0, le=5)
    delivery_rating: float = Field(0.0, ge=0, le=5)
    price_rating: float = Field(0.0, ge=0, le=5)
    service_rating: float = Field(0.0, ge=0, le=5)
    communication_rating: float = Field(0.0, ge=0, le=5)
    orders_placed: int = Field(0, ge=0)
    orders_completed: int = Field(0, ge=0)
    orders_on_time: int = Field(0, ge=0)
    defect_count: int = Field(0, ge=0)
    total_value: float = Field(0.0, ge=0)
    evaluated_by: Optional[str] = Field(None, max_length=200)
    comments: Optional[str] = None


class VendorRatingCreate(VendorRatingBase):
    """Schema for creating a vendor rating."""

    pass


class VendorRatingUpdate(BaseModel):
    """Schema for updating a vendor rating."""

    quality_rating: Optional[float] = Field(None, ge=0, le=5)
    delivery_rating: Optional[float] = Field(None, ge=0, le=5)
    price_rating: Optional[float] = Field(None, ge=0, le=5)
    service_rating: Optional[float] = Field(None, ge=0, le=5)
    communication_rating: Optional[float] = Field(None, ge=0, le=5)
    orders_placed: Optional[int] = Field(None, ge=0)
    orders_completed: Optional[int] = Field(None, ge=0)
    orders_on_time: Optional[int] = Field(None, ge=0)
    defect_count: Optional[int] = Field(None, ge=0)
    total_value: Optional[float] = Field(None, ge=0)
    evaluated_by: Optional[str] = Field(None, max_length=200)
    comments: Optional[str] = None


class VendorRatingResponse(BaseModel):
    """Schema for vendor rating response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor_id: int
    rating_period: str
    quality_rating: float
    delivery_rating: float
    price_rating: float
    service_rating: float
    communication_rating: float
    overall_rating: float
    orders_placed: int
    orders_completed: int
    orders_on_time: int
    defect_count: int
    total_value: float
    evaluated_by: Optional[str] = None
    evaluation_date: Optional[datetime] = None
    comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Vendor Schemas
class VendorBase(BaseModel):
    """Base schema for vendor."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    legal_name: Optional[str] = Field(None, max_length=200)
    tax_id: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=100)

    # Address
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)

    # Contact
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    fax: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=200)

    # Category
    category_id: Optional[int] = None

    # Details
    description: Optional[str] = None
    notes: Optional[str] = None


class VendorCreate(VendorBase):
    """Schema for creating a vendor."""

    status: VendorStatus = VendorStatus.PENDING


class VendorUpdate(BaseModel):
    """Schema for updating a vendor."""

    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    legal_name: Optional[str] = Field(None, max_length=200)
    tax_id: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=100)

    # Address
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)

    # Contact
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    fax: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=200)

    # Category
    category_id: Optional[int] = None

    # Status
    status: Optional[VendorStatus] = None

    # Details
    description: Optional[str] = None
    notes: Optional[str] = None


class VendorResponse(VendorBase):
    """Schema for vendor response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    average_rating: float
    total_orders: int
    on_time_delivery_rate: float
    quality_score: float
    registered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Related data
    category: Optional[VendorCategoryResponse] = None
    certifications: List[VendorCertificationResponse] = []
    contacts: List[VendorContactResponse] = []


class VendorListResponse(BaseModel):
    """Schema for vendor list item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    email: str
    status: str
    category_id: Optional[int] = None
    average_rating: float
    total_orders: int
    city: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime


class VendorFilterParams(FilterParams):
    """Filter parameters for vendor list."""

    status: Optional[VendorStatus] = None
    category_id: Optional[int] = None
    country: Optional[str] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    has_certification: Optional[CertificationType] = None
