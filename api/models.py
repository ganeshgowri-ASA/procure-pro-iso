"""
Database Models Module
SQLAlchemy ORM models for the procurement system
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date,
    Text, ForeignKey, Numeric, ARRAY, JSON
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


# ============================================
# MIXINS
# ============================================

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())


class UUIDMixin:
    """Mixin for UUID primary key."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


# ============================================
# USER MODELS
# ============================================

class User(Base, UUIDMixin, TimestampMixin):
    """User model for authentication and authorization."""
    __tablename__ = 'users'

    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    department = Column(String(100))
    role = Column(String(50), nullable=False, default='user')
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User {self.email}>"


class UserRole(Base, UUIDMixin):
    """User role with permissions."""
    __tablename__ = 'user_roles'

    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), default=func.now())


# ============================================
# ORGANIZATION MODELS
# ============================================

class Organization(Base, UUIDMixin, TimestampMixin):
    """Organization model."""
    __tablename__ = 'organizations'

    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True)
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    phone = Column(String(50))
    email = Column(String(255))
    website = Column(String(255))
    logo_url = Column(String(500))
    is_active = Column(Boolean, default=True)

    departments = relationship("Department", back_populates="organization")


class Department(Base, UUIDMixin, TimestampMixin):
    """Department model."""
    __tablename__ = 'departments'

    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'))
    name = Column(String(255), nullable=False)
    code = Column(String(50))
    manager_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    budget_limit = Column(Numeric(15, 2))
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="departments")


# ============================================
# PROJECT MODELS
# ============================================

class Project(Base, UUIDMixin, TimestampMixin):
    """Project model."""
    __tablename__ = 'projects'

    project_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    client_name = Column(String(255))
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'))
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'))
    project_manager_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    status = Column(String(50), default='active')
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Numeric(15, 2))
    currency = Column(String(3), default='USD')
    location = Column(String(255))
    is_iso_compliant = Column(Boolean, default=True)
    metadata = Column(JSONB, default={})

    rfqs = relationship("RFQ", back_populates="project")
    purchase_orders = relationship("PurchaseOrder", back_populates="project")

    def __repr__(self):
        return f"<Project {self.project_number}: {self.name}>"


# ============================================
# VENDOR MODELS
# ============================================

class Vendor(Base, UUIDMixin, TimestampMixin):
    """Vendor/Supplier model."""
    __tablename__ = 'vendors'

    vendor_code = Column(String(50), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    trade_name = Column(String(255))
    contact_person = Column(String(255))
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    fax = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    website = Column(String(255))
    tax_id = Column(String(50))
    registration_number = Column(String(100))
    bank_name = Column(String(255))
    bank_account = Column(String(100))
    bank_swift = Column(String(50))
    payment_terms = Column(String(100))
    credit_limit = Column(Numeric(15, 2))
    rating = Column(Numeric(3, 2))
    vendor_type = Column(String(50))
    categories = Column(ARRAY(Text))
    certifications = Column(ARRAY(Text))
    is_approved = Column(Boolean, default=False)
    is_blacklisted = Column(Boolean, default=False)
    approval_date = Column(Date)
    blacklist_reason = Column(Text)
    notes = Column(Text)
    metadata = Column(JSONB, default={})

    quotations = relationship("Quotation", back_populates="vendor")
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")

    def __repr__(self):
        return f"<Vendor {self.vendor_code}: {self.company_name}>"


# ============================================
# ITEM MODELS
# ============================================

class ItemCategory(Base, UUIDMixin):
    """Item category model."""
    __tablename__ = 'item_categories'

    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('item_categories.id'))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now())


class UnitOfMeasure(Base, UUIDMixin):
    """Unit of measure model."""
    __tablename__ = 'units_of_measure'

    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)


class Item(Base, UUIDMixin, TimestampMixin):
    """Item/Material model."""
    __tablename__ = 'items'

    item_code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    specifications = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey('item_categories.id'))
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units_of_measure.id'))
    brand = Column(String(100))
    model = Column(String(100))
    manufacturer = Column(String(255))
    part_number = Column(String(100))
    hs_code = Column(String(20))
    standard_price = Column(Numeric(15, 2))
    currency = Column(String(3), default='USD')
    lead_time_days = Column(Integer)
    min_order_qty = Column(Numeric(15, 3))
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB, default={})

    def __repr__(self):
        return f"<Item {self.item_code}: {self.name}>"


# ============================================
# RFQ MODELS
# ============================================

class RFQ(Base, UUIDMixin, TimestampMixin):
    """Request for Quotation model."""
    __tablename__ = 'rfqs'

    rfq_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'))
    requested_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    status = Column(String(50), default='draft')
    rfq_type = Column(String(50), default='standard')
    priority = Column(String(20), default='normal')
    issue_date = Column(Date)
    closing_date = Column(Date)
    validity_days = Column(Integer, default=30)
    delivery_location = Column(String(255))
    delivery_terms = Column(String(100))
    payment_terms = Column(String(100))
    currency = Column(String(3), default='USD')
    estimated_value = Column(Numeric(15, 2))
    terms_and_conditions = Column(Text)
    special_instructions = Column(Text)
    attachments = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})

    project = relationship("Project", back_populates="rfqs")
    items = relationship("RFQItem", back_populates="rfq", cascade="all, delete-orphan")
    quotations = relationship("Quotation", back_populates="rfq")

    def __repr__(self):
        return f"<RFQ {self.rfq_number}: {self.title}>"


class RFQItem(Base, UUIDMixin):
    """RFQ line item model."""
    __tablename__ = 'rfq_items'

    rfq_id = Column(UUID(as_uuid=True), ForeignKey('rfqs.id', ondelete='CASCADE'))
    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id'))
    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    specifications = Column(Text)
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units_of_measure.id'))
    target_price = Column(Numeric(15, 2))
    required_delivery_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())

    rfq = relationship("RFQ", back_populates="items")


# ============================================
# QUOTATION MODELS
# ============================================

class Quotation(Base, UUIDMixin, TimestampMixin):
    """Vendor quotation model."""
    __tablename__ = 'quotations'

    quotation_number = Column(String(50), unique=True, nullable=False)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey('rfqs.id'))
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.id'))
    submitted_by = Column(String(255))
    status = Column(String(50), default='submitted')
    submission_date = Column(DateTime(timezone=True), default=func.now())
    validity_date = Column(Date)
    currency = Column(String(3), default='USD')
    subtotal = Column(Numeric(15, 2))
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    tax_percent = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    shipping_cost = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2))
    payment_terms = Column(String(255))
    delivery_terms = Column(String(255))
    delivery_days = Column(Integer)
    warranty_terms = Column(Text)
    notes = Column(Text)
    attachments = Column(JSONB, default=[])
    is_technically_compliant = Column(Boolean)
    technical_score = Column(Numeric(5, 2))
    commercial_score = Column(Numeric(5, 2))
    overall_score = Column(Numeric(5, 2))
    rank = Column(Integer)
    is_selected = Column(Boolean, default=False)
    metadata = Column(JSONB, default={})

    rfq = relationship("RFQ", back_populates="quotations")
    vendor = relationship("Vendor", back_populates="quotations")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quotation {self.quotation_number}>"


class QuotationItem(Base, UUIDMixin):
    """Quotation line item model."""
    __tablename__ = 'quotation_items'

    quotation_id = Column(UUID(as_uuid=True), ForeignKey('quotations.id', ondelete='CASCADE'))
    rfq_item_id = Column(UUID(as_uuid=True), ForeignKey('rfq_items.id'))
    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_price = Column(Numeric(15, 4), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    brand_offered = Column(String(100))
    model_offered = Column(String(100))
    country_of_origin = Column(String(100))
    lead_time_days = Column(Integer)
    is_compliant = Column(Boolean, default=True)
    compliance_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())

    quotation = relationship("Quotation", back_populates="items")


# ============================================
# TBE MODELS
# ============================================

class TBEEvaluation(Base, UUIDMixin, TimestampMixin):
    """Technical Bid Evaluation model."""
    __tablename__ = 'tbe_evaluations'

    evaluation_number = Column(String(50), unique=True, nullable=False)
    rfq_id = Column(UUID(as_uuid=True), ForeignKey('rfqs.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    evaluated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    status = Column(String(50), default='draft')
    evaluation_date = Column(Date)
    weight_price = Column(Numeric(5, 2), default=0.40)
    weight_quality = Column(Numeric(5, 2), default=0.25)
    weight_delivery = Column(Numeric(5, 2), default=0.20)
    weight_compliance = Column(Numeric(5, 2), default=0.15)
    recommendation = Column(Text)
    selected_vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.id'))
    attachments = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})

    def __repr__(self):
        return f"<TBEEvaluation {self.evaluation_number}>"


# ============================================
# PURCHASE ORDER MODELS
# ============================================

class PurchaseOrder(Base, UUIDMixin, TimestampMixin):
    """Purchase Order model."""
    __tablename__ = 'purchase_orders'

    po_number = Column(String(50), unique=True, nullable=False)
    revision = Column(Integer, default=0)
    quotation_id = Column(UUID(as_uuid=True), ForeignKey('quotations.id'))
    rfq_id = Column(UUID(as_uuid=True), ForeignKey('rfqs.id'))
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.id'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    status = Column(String(50), default='draft')
    po_date = Column(Date, default=func.current_date())
    delivery_date = Column(Date)
    currency = Column(String(3), default='USD')
    exchange_rate = Column(Numeric(15, 6), default=1)
    subtotal = Column(Numeric(15, 2))
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    tax_percent = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    shipping_cost = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2))
    amount_paid = Column(Numeric(15, 2), default=0)
    payment_terms = Column(String(255))
    payment_method = Column(String(100))
    delivery_terms = Column(String(255))
    delivery_address = Column(Text)
    shipping_method = Column(String(100))
    warranty_terms = Column(Text)
    terms_and_conditions = Column(Text)
    notes = Column(Text)
    internal_notes = Column(Text)
    attachments = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})

    project = relationship("Project", back_populates="purchase_orders")
    vendor = relationship("Vendor", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PurchaseOrder {self.po_number}>"


class PurchaseOrderItem(Base, UUIDMixin):
    """Purchase Order line item model."""
    __tablename__ = 'purchase_order_items'

    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey('purchase_orders.id', ondelete='CASCADE'))
    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id'))
    quotation_item_id = Column(UUID(as_uuid=True), ForeignKey('quotation_items.id'))
    line_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    specifications = Column(Text)
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units_of_measure.id'))
    unit_price = Column(Numeric(15, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    tax_percent = Column(Numeric(5, 2), default=0)
    total_price = Column(Numeric(15, 2), nullable=False)
    quantity_received = Column(Numeric(15, 3), default=0)
    quantity_invoiced = Column(Numeric(15, 3), default=0)
    delivery_date = Column(Date)
    status = Column(String(50), default='pending')
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())

    purchase_order = relationship("PurchaseOrder", back_populates="items")


# ============================================
# AUDIT LOG MODEL
# ============================================

class AuditLog(Base, UUIDMixin):
    """Audit log for tracking all changes."""
    __tablename__ = 'audit_logs'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
