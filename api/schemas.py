"""
API Schemas Module
Pydantic/Marshmallow schemas for request/response validation
"""

from datetime import date, datetime
from typing import Optional, List, Any
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr, validator
from uuid import UUID


# ============================================
# BASE SCHEMAS
# ============================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None,
            UUID: lambda v: str(v) if v else None
        }


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    data: List[Any]
    pagination: dict


# ============================================
# USER SCHEMAS
# ============================================

class UserBase(BaseSchema):
    """Base user schema."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    department: Optional[str] = None
    role: str = Field(default='user')


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    """Schema for updating a user."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""
    id: UUID
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime


# ============================================
# PROJECT SCHEMAS
# ============================================

class ProjectBase(BaseSchema):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = None
    status: str = Field(default='active')
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    currency: str = Field(default='USD', max_length=3)
    location: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    organization_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    project_manager_id: Optional[UUID] = None


class ProjectUpdate(BaseSchema):
    """Schema for updating a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    client_name: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    location: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: UUID
    project_number: str
    is_iso_compliant: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ============================================
# VENDOR SCHEMAS
# ============================================

class VendorBase(BaseSchema):
    """Base vendor schema."""
    company_name: str = Field(..., min_length=1, max_length=255)
    trade_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    vendor_type: Optional[str] = None
    notes: Optional[str] = None


class VendorCreate(VendorBase):
    """Schema for creating a vendor."""
    categories: Optional[List[str]] = None
    certifications: Optional[List[str]] = None


class VendorUpdate(BaseSchema):
    """Schema for updating a vendor."""
    company_name: Optional[str] = None
    trade_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None


class VendorResponse(VendorBase):
    """Vendor response schema."""
    id: UUID
    vendor_code: str
    is_approved: bool
    is_blacklisted: bool
    rating: Optional[float] = None
    approval_date: Optional[date] = None
    created_at: datetime


# ============================================
# ITEM SCHEMAS
# ============================================

class ItemBase(BaseSchema):
    """Base item schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    specifications: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    part_number: Optional[str] = None
    standard_price: Optional[Decimal] = None
    currency: str = Field(default='USD')
    lead_time_days: Optional[int] = None
    min_order_qty: Optional[Decimal] = None


class ItemCreate(ItemBase):
    """Schema for creating an item."""
    category_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    hs_code: Optional[str] = None


class ItemResponse(ItemBase):
    """Item response schema."""
    id: UUID
    item_code: str
    is_active: bool
    created_at: datetime


# ============================================
# RFQ SCHEMAS
# ============================================

class RFQItemBase(BaseSchema):
    """Base RFQ item schema."""
    description: str
    specifications: Optional[str] = None
    quantity: Decimal
    target_price: Optional[Decimal] = None
    required_delivery_date: Optional[date] = None
    notes: Optional[str] = None


class RFQItemCreate(RFQItemBase):
    """Schema for creating an RFQ item."""
    item_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None


class RFQBase(BaseSchema):
    """Base RFQ schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rfq_type: str = Field(default='standard')
    priority: str = Field(default='normal')
    issue_date: Optional[date] = None
    closing_date: Optional[date] = None
    validity_days: int = Field(default=30)
    delivery_location: Optional[str] = None
    delivery_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    currency: str = Field(default='USD')
    estimated_value: Optional[Decimal] = None
    terms_and_conditions: Optional[str] = None
    special_instructions: Optional[str] = None


class RFQCreate(RFQBase):
    """Schema for creating an RFQ."""
    project_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    items: Optional[List[RFQItemCreate]] = None
    vendor_ids: Optional[List[UUID]] = None


class RFQUpdate(BaseSchema):
    """Schema for updating an RFQ."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    closing_date: Optional[date] = None
    terms_and_conditions: Optional[str] = None


class RFQResponse(RFQBase):
    """RFQ response schema."""
    id: UUID
    rfq_number: str
    status: str
    created_at: datetime
    item_count: Optional[int] = None
    quotation_count: Optional[int] = None


# ============================================
# QUOTATION SCHEMAS
# ============================================

class QuotationItemBase(BaseSchema):
    """Base quotation item schema."""
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal = Field(default=0)
    brand_offered: Optional[str] = None
    model_offered: Optional[str] = None
    country_of_origin: Optional[str] = None
    lead_time_days: Optional[int] = None
    is_compliant: bool = Field(default=True)
    compliance_notes: Optional[str] = None


class QuotationItemCreate(QuotationItemBase):
    """Schema for creating a quotation item."""
    rfq_item_id: Optional[UUID] = None


class QuotationBase(BaseSchema):
    """Base quotation schema."""
    validity_date: Optional[date] = None
    currency: str = Field(default='USD')
    discount_percent: Decimal = Field(default=0)
    tax_percent: Decimal = Field(default=0)
    shipping_cost: Decimal = Field(default=0)
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    delivery_days: Optional[int] = None
    warranty_terms: Optional[str] = None
    notes: Optional[str] = None


class QuotationCreate(QuotationBase):
    """Schema for creating a quotation."""
    rfq_id: UUID
    vendor_id: UUID
    items: List[QuotationItemCreate]


class QuotationResponse(QuotationBase):
    """Quotation response schema."""
    id: UUID
    quotation_number: str
    rfq_id: UUID
    vendor_id: UUID
    status: str
    submission_date: datetime
    subtotal: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    overall_score: Optional[float] = None
    rank: Optional[int] = None
    is_selected: bool


# ============================================
# TBE SCHEMAS
# ============================================

class TBECriteriaBase(BaseSchema):
    """Base TBE criteria schema."""
    criteria_name: str
    category: str
    weight: Decimal
    max_score: Decimal = Field(default=100)
    description: Optional[str] = None
    evaluation_method: Optional[str] = None


class TBEScoreBase(BaseSchema):
    """Base TBE score schema."""
    criteria_id: UUID
    quotation_id: UUID
    score: Decimal
    comments: Optional[str] = None


class TBEEvaluationBase(BaseSchema):
    """Base TBE evaluation schema."""
    title: str
    description: Optional[str] = None
    weight_price: Decimal = Field(default=0.40)
    weight_quality: Decimal = Field(default=0.25)
    weight_delivery: Decimal = Field(default=0.20)
    weight_compliance: Decimal = Field(default=0.15)


class TBEEvaluationCreate(TBEEvaluationBase):
    """Schema for creating a TBE evaluation."""
    rfq_id: UUID
    criteria: Optional[List[TBECriteriaBase]] = None


class TBEEvaluationResponse(TBEEvaluationBase):
    """TBE evaluation response schema."""
    id: UUID
    evaluation_number: str
    rfq_id: UUID
    status: str
    evaluation_date: Optional[date] = None
    recommendation: Optional[str] = None
    selected_vendor_id: Optional[UUID] = None
    created_at: datetime


# ============================================
# PURCHASE ORDER SCHEMAS
# ============================================

class POItemBase(BaseSchema):
    """Base PO item schema."""
    description: str
    specifications: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal = Field(default=0)
    tax_percent: Decimal = Field(default=0)
    delivery_date: Optional[date] = None
    notes: Optional[str] = None


class POItemCreate(POItemBase):
    """Schema for creating a PO item."""
    item_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    quotation_item_id: Optional[UUID] = None


class PurchaseOrderBase(BaseSchema):
    """Base purchase order schema."""
    po_date: date = Field(default_factory=date.today)
    delivery_date: Optional[date] = None
    currency: str = Field(default='USD')
    discount_percent: Decimal = Field(default=0)
    tax_percent: Decimal = Field(default=0)
    shipping_cost: Decimal = Field(default=0)
    payment_terms: Optional[str] = None
    payment_method: Optional[str] = None
    delivery_terms: Optional[str] = None
    delivery_address: Optional[str] = None
    shipping_method: Optional[str] = None
    warranty_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating a purchase order."""
    vendor_id: UUID
    project_id: Optional[UUID] = None
    rfq_id: Optional[UUID] = None
    quotation_id: Optional[UUID] = None
    items: List[POItemCreate]


class PurchaseOrderUpdate(BaseSchema):
    """Schema for updating a purchase order."""
    status: Optional[str] = None
    delivery_date: Optional[date] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    """Purchase order response schema."""
    id: UUID
    po_number: str
    revision: int
    vendor_id: UUID
    status: str
    subtotal: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    amount_paid: Decimal
    created_at: datetime


# ============================================
# REPORT SCHEMAS
# ============================================

class DashboardResponse(BaseSchema):
    """Dashboard summary response."""
    active_projects: int
    open_rfqs: int
    active_pos: int
    approved_vendors: int
    total_po_value: Decimal
    recent_quotations: int


class ProcurementSummaryResponse(BaseSchema):
    """Procurement summary report response."""
    total_orders: int
    total_value: Decimal
    average_order_value: Decimal
    unique_vendors: int


class VendorPerformanceResponse(BaseSchema):
    """Vendor performance report response."""
    vendor_id: UUID
    vendor_name: str
    total_orders: int
    on_time_percentage: float
    quality_score: float
    overall_score: float
