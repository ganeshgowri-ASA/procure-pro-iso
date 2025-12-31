"""Pydantic schemas for RFQ Workflow API."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.core.pagination import FilterParams
from app.models.rfq import RFQStatus, InvitationStatus, QuotationStatus


# RFQ Item Schemas
class RFQItemBase(BaseModel):
    """Base schema for RFQ item."""

    item_number: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)

    # Specifications
    specifications: Optional[str] = None
    brand_preference: Optional[str] = Field(None, max_length=200)
    model_preference: Optional[str] = Field(None, max_length=200)
    part_number: Optional[str] = Field(None, max_length=100)

    # Requirements
    required_delivery_date: Optional[datetime] = None
    is_mandatory: bool = True
    alternative_allowed: bool = False

    # Budget
    estimated_unit_price: Optional[float] = Field(None, ge=0)
    budget_amount: Optional[float] = Field(None, ge=0)

    notes: Optional[str] = None


class RFQItemCreate(RFQItemBase):
    """Schema for creating an RFQ item."""

    pass


class RFQItemUpdate(BaseModel):
    """Schema for updating an RFQ item."""

    item_number: Optional[int] = Field(None, ge=1)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    specifications: Optional[str] = None
    brand_preference: Optional[str] = Field(None, max_length=200)
    model_preference: Optional[str] = Field(None, max_length=200)
    part_number: Optional[str] = Field(None, max_length=100)
    required_delivery_date: Optional[datetime] = None
    is_mandatory: Optional[bool] = None
    alternative_allowed: Optional[bool] = None
    estimated_unit_price: Optional[float] = Field(None, ge=0)
    budget_amount: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class RFQItemResponse(RFQItemBase):
    """Schema for RFQ item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    rfq_id: int
    created_at: datetime
    updated_at: datetime


# RFQ Vendor Invitation Schemas
class RFQVendorInvitationCreate(BaseModel):
    """Schema for creating vendor invitation."""

    vendor_id: int
    notes: Optional[str] = None


class RFQVendorInvitationResponse(BaseModel):
    """Schema for vendor invitation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    rfq_id: int
    vendor_id: int
    status: str
    invited_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    decline_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Vendor info
    vendor_name: Optional[str] = None
    vendor_email: Optional[str] = None


class RFQVendorInvitationUpdate(BaseModel):
    """Schema for updating vendor invitation."""

    status: Optional[InvitationStatus] = None
    decline_reason: Optional[str] = None
    notes: Optional[str] = None


# Quotation Item Schemas
class QuotationItemBase(BaseModel):
    """Base schema for quotation item."""

    rfq_item_id: int
    unit_price: float = Field(..., ge=0)
    quantity: float = Field(..., gt=0)

    # Offered product
    offered_brand: Optional[str] = Field(None, max_length=200)
    offered_model: Optional[str] = Field(None, max_length=200)
    offered_part_number: Optional[str] = Field(None, max_length=100)
    is_alternative: bool = False

    # Delivery
    lead_time_days: Optional[int] = Field(None, ge=0)
    availability: Optional[str] = Field(None, max_length=100)

    specifications: Optional[str] = None
    notes: Optional[str] = None


class QuotationItemCreate(QuotationItemBase):
    """Schema for creating a quotation item."""

    pass


class QuotationItemUpdate(BaseModel):
    """Schema for updating a quotation item."""

    unit_price: Optional[float] = Field(None, ge=0)
    quantity: Optional[float] = Field(None, gt=0)
    offered_brand: Optional[str] = Field(None, max_length=200)
    offered_model: Optional[str] = Field(None, max_length=200)
    offered_part_number: Optional[str] = Field(None, max_length=100)
    is_alternative: Optional[bool] = None
    lead_time_days: Optional[int] = Field(None, ge=0)
    availability: Optional[str] = Field(None, max_length=100)
    specifications: Optional[str] = None
    notes: Optional[str] = None


class QuotationItemResponse(BaseModel):
    """Schema for quotation item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    quotation_id: int
    rfq_item_id: int
    unit_price: float
    quantity: float
    total_price: float
    offered_brand: Optional[str] = None
    offered_model: Optional[str] = None
    offered_part_number: Optional[str] = None
    is_alternative: bool
    lead_time_days: Optional[int] = None
    availability: Optional[str] = None
    specifications: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # RFQ item info
    rfq_item_name: Optional[str] = None
    rfq_item_number: Optional[int] = None


# Quotation Schemas
class QuotationBase(BaseModel):
    """Base schema for quotation."""

    # Pricing
    discount_percentage: float = Field(0.0, ge=0, le=100)
    tax_percentage: float = Field(0.0, ge=0)
    shipping_cost: float = Field(0.0, ge=0)
    currency: str = Field("USD", max_length=10)

    # Terms
    validity_days: int = Field(30, ge=1)
    delivery_days: Optional[int] = Field(None, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=200)
    warranty_terms: Optional[str] = None

    document_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class QuotationCreate(QuotationBase):
    """Schema for creating a quotation."""

    vendor_id: int
    items: List[QuotationItemCreate] = []


class QuotationUpdate(BaseModel):
    """Schema for updating a quotation."""

    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    tax_percentage: Optional[float] = Field(None, ge=0)
    shipping_cost: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    validity_days: Optional[int] = Field(None, ge=1)
    delivery_days: Optional[int] = Field(None, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=200)
    warranty_terms: Optional[str] = None
    document_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class QuotationSubmit(BaseModel):
    """Schema for submitting a quotation."""

    pass  # Quotation is submitted by changing status


class QuotationEvaluate(BaseModel):
    """Schema for evaluating a quotation."""

    technical_score: float = Field(..., ge=0, le=100)
    commercial_score: float = Field(..., ge=0, le=100)
    evaluation_notes: Optional[str] = None
    evaluated_by: Optional[str] = Field(None, max_length=200)


class QuotationResponse(QuotationBase):
    """Schema for quotation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    rfq_id: int
    vendor_id: int
    quotation_number: str
    status: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    technical_score: Optional[float] = None
    commercial_score: Optional[float] = None
    overall_score: Optional[float] = None
    evaluation_notes: Optional[str] = None
    evaluated_by: Optional[str] = None
    evaluated_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Related data
    items: List[QuotationItemResponse] = []
    vendor_name: Optional[str] = None


# RFQ Schemas
class RFQBase(BaseModel):
    """Base schema for RFQ."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    # Dates
    submission_deadline: Optional[datetime] = None
    validity_period_days: int = Field(30, ge=1)

    # Requirements
    delivery_address: Optional[str] = None
    delivery_terms: Optional[str] = Field(None, max_length=100)
    payment_terms: Optional[str] = Field(None, max_length=200)
    warranty_requirements: Optional[str] = None
    technical_requirements: Optional[str] = None
    compliance_requirements: Optional[str] = None

    # Budget
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    currency: str = Field("USD", max_length=10)

    # Metadata
    department: Optional[str] = Field(None, max_length=100)
    project_reference: Optional[str] = Field(None, max_length=100)
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")
    notes: Optional[str] = None


class RFQCreate(RFQBase):
    """Schema for creating an RFQ."""

    items: List[RFQItemCreate] = []
    vendor_ids: List[int] = []


class RFQUpdate(BaseModel):
    """Schema for updating an RFQ."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    validity_period_days: Optional[int] = Field(None, ge=1)
    delivery_address: Optional[str] = None
    delivery_terms: Optional[str] = Field(None, max_length=100)
    payment_terms: Optional[str] = Field(None, max_length=200)
    warranty_requirements: Optional[str] = None
    technical_requirements: Optional[str] = None
    compliance_requirements: Optional[str] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    department: Optional[str] = Field(None, max_length=100)
    project_reference: Optional[str] = Field(None, max_length=100)
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    notes: Optional[str] = None


class RFQStatusUpdate(BaseModel):
    """Schema for updating RFQ status."""

    status: RFQStatus
    notes: Optional[str] = None


class RFQResponse(RFQBase):
    """Schema for RFQ response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    rfq_number: str
    status: str
    issue_date: Optional[datetime] = None
    created_by: Optional[str] = None
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Related data
    items: List[RFQItemResponse] = []
    vendor_invitations: List[RFQVendorInvitationResponse] = []
    quotations_count: int = 0


class RFQListResponse(BaseModel):
    """Schema for RFQ list item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    rfq_number: str
    title: str
    status: str
    submission_deadline: Optional[datetime] = None
    priority: str
    department: Optional[str] = None
    items_count: int = 0
    vendors_invited: int = 0
    quotations_received: int = 0
    created_at: datetime


class RFQFilterParams(FilterParams):
    """Filter parameters for RFQ list."""

    status: Optional[RFQStatus] = None
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    department: Optional[str] = None
    created_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Quote Comparison Schemas
class QuoteItemComparison(BaseModel):
    """Comparison of a single RFQ item across vendors."""

    rfq_item_id: int
    rfq_item_name: str
    rfq_item_number: int
    requested_quantity: float
    unit: str
    estimated_price: Optional[float] = None

    # Vendor quotes for this item
    quotes: List[dict]  # Contains vendor_id, vendor_name, unit_price, total_price, etc.

    # Analysis
    lowest_price: float
    highest_price: float
    average_price: float
    price_variance_percentage: float


class QuoteComparisonResponse(BaseModel):
    """Quote comparison analysis for an RFQ."""

    rfq_id: int
    rfq_number: str
    rfq_title: str

    # Summary
    total_vendors_invited: int
    total_quotations_received: int
    quotations_under_evaluation: int

    # Overall comparison
    quotations: List[QuotationResponse]

    # Item-by-item comparison
    item_comparisons: List[QuoteItemComparison]

    # Recommendations
    lowest_total_quote: Optional[dict] = None
    best_rated_vendor: Optional[dict] = None
    fastest_delivery: Optional[dict] = None
