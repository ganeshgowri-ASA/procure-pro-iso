-- ============================================
-- Procure-Pro-ISO Database Schema
-- Comprehensive Procurement Management System
-- PostgreSQL Database Schema
-- Version: 1.0.0
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- 1. USERS AND AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    department VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. ORGANIZATIONS AND DEPARTMENTS
-- ============================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    manager_id UUID REFERENCES users(id),
    budget_limit DECIMAL(15, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. PROJECTS
-- ============================================

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    client_name VARCHAR(255),
    organization_id UUID REFERENCES organizations(id),
    department_id UUID REFERENCES departments(id),
    project_manager_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    location VARCHAR(255),
    is_iso_compliant BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_number ON projects(project_number);

-- ============================================
-- 4. VENDORS / SUPPLIERS
-- ============================================

CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_code VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255),
    contact_person VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    fax VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    website VARCHAR(255),
    tax_id VARCHAR(50),
    registration_number VARCHAR(100),
    bank_name VARCHAR(255),
    bank_account VARCHAR(100),
    bank_swift VARCHAR(50),
    payment_terms VARCHAR(100),
    credit_limit DECIMAL(15, 2),
    rating DECIMAL(3, 2),
    vendor_type VARCHAR(50),
    categories TEXT[],
    certifications TEXT[],
    is_approved BOOLEAN DEFAULT FALSE,
    is_blacklisted BOOLEAN DEFAULT FALSE,
    approval_date DATE,
    blacklist_reason TEXT,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vendors_code ON vendors(vendor_code);
CREATE INDEX idx_vendors_name ON vendors(company_name);
CREATE INDEX idx_vendors_approved ON vendors(is_approved);

-- ============================================
-- 5. ITEM CATEGORIES AND ITEMS
-- ============================================

CREATE TABLE item_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE,
    parent_id UUID REFERENCES item_categories(id),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE units_of_measure (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    specifications TEXT,
    category_id UUID REFERENCES item_categories(id),
    unit_id UUID REFERENCES units_of_measure(id),
    brand VARCHAR(100),
    model VARCHAR(100),
    manufacturer VARCHAR(255),
    part_number VARCHAR(100),
    hs_code VARCHAR(20),
    standard_price DECIMAL(15, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    lead_time_days INTEGER,
    min_order_qty DECIMAL(15, 3),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_items_code ON items(item_code);
CREATE INDEX idx_items_category ON items(category_id);

-- ============================================
-- 6. RFQ (REQUEST FOR QUOTATION)
-- ============================================

CREATE TABLE rfqs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfq_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    project_id UUID REFERENCES projects(id),
    department_id UUID REFERENCES departments(id),
    requested_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'draft',
    rfq_type VARCHAR(50) DEFAULT 'standard',
    priority VARCHAR(20) DEFAULT 'normal',
    issue_date DATE,
    closing_date DATE,
    validity_days INTEGER DEFAULT 30,
    delivery_location VARCHAR(255),
    delivery_terms VARCHAR(100),
    payment_terms VARCHAR(100),
    currency VARCHAR(3) DEFAULT 'USD',
    estimated_value DECIMAL(15, 2),
    terms_and_conditions TEXT,
    special_instructions TEXT,
    attachments JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rfqs_number ON rfqs(rfq_number);
CREATE INDEX idx_rfqs_status ON rfqs(status);
CREATE INDEX idx_rfqs_project ON rfqs(project_id);

CREATE TABLE rfq_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfq_id UUID REFERENCES rfqs(id) ON DELETE CASCADE,
    item_id UUID REFERENCES items(id),
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    specifications TEXT,
    quantity DECIMAL(15, 3) NOT NULL,
    unit_id UUID REFERENCES units_of_measure(id),
    target_price DECIMAL(15, 2),
    required_delivery_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rfq_items_rfq ON rfq_items(rfq_id);

CREATE TABLE rfq_vendors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfq_id UUID REFERENCES rfqs(id) ON DELETE CASCADE,
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    invited_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_date TIMESTAMP WITH TIME ZONE,
    declined BOOLEAN DEFAULT FALSE,
    decline_reason TEXT,
    UNIQUE(rfq_id, vendor_id)
);

-- ============================================
-- 7. QUOTATIONS / BIDS
-- ============================================

CREATE TABLE quotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_number VARCHAR(50) UNIQUE NOT NULL,
    rfq_id UUID REFERENCES rfqs(id),
    vendor_id UUID REFERENCES vendors(id),
    submitted_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'submitted',
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    validity_date DATE,
    currency VARCHAR(3) DEFAULT 'USD',
    subtotal DECIMAL(15, 2),
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    tax_percent DECIMAL(5, 2) DEFAULT 0,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_cost DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2),
    payment_terms VARCHAR(255),
    delivery_terms VARCHAR(255),
    delivery_days INTEGER,
    warranty_terms TEXT,
    notes TEXT,
    attachments JSONB DEFAULT '[]',
    is_technically_compliant BOOLEAN,
    technical_score DECIMAL(5, 2),
    commercial_score DECIMAL(5, 2),
    overall_score DECIMAL(5, 2),
    rank INTEGER,
    is_selected BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quotations_rfq ON quotations(rfq_id);
CREATE INDEX idx_quotations_vendor ON quotations(vendor_id);
CREATE INDEX idx_quotations_status ON quotations(status);

CREATE TABLE quotation_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES quotations(id) ON DELETE CASCADE,
    rfq_item_id UUID REFERENCES rfq_items(id),
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(15, 3) NOT NULL,
    unit_price DECIMAL(15, 4) NOT NULL,
    total_price DECIMAL(15, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    brand_offered VARCHAR(100),
    model_offered VARCHAR(100),
    country_of_origin VARCHAR(100),
    lead_time_days INTEGER,
    is_compliant BOOLEAN DEFAULT TRUE,
    compliance_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quotation_items_quotation ON quotation_items(quotation_id);

-- ============================================
-- 8. TBE (TECHNICAL BID EVALUATION)
-- ============================================

CREATE TABLE tbe_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_number VARCHAR(50) UNIQUE NOT NULL,
    rfq_id UUID REFERENCES rfqs(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    evaluated_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'draft',
    evaluation_date DATE,
    weight_price DECIMAL(5, 2) DEFAULT 0.40,
    weight_quality DECIMAL(5, 2) DEFAULT 0.25,
    weight_delivery DECIMAL(5, 2) DEFAULT 0.20,
    weight_compliance DECIMAL(5, 2) DEFAULT 0.15,
    recommendation TEXT,
    selected_vendor_id UUID REFERENCES vendors(id),
    attachments JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tbe_rfq ON tbe_evaluations(rfq_id);

CREATE TABLE tbe_criteria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tbe_id UUID REFERENCES tbe_evaluations(id) ON DELETE CASCADE,
    criteria_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    weight DECIMAL(5, 2) NOT NULL,
    max_score DECIMAL(5, 2) DEFAULT 100,
    description TEXT,
    evaluation_method TEXT,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE tbe_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tbe_id UUID REFERENCES tbe_evaluations(id) ON DELETE CASCADE,
    criteria_id UUID REFERENCES tbe_criteria(id) ON DELETE CASCADE,
    quotation_id UUID REFERENCES quotations(id) ON DELETE CASCADE,
    score DECIMAL(5, 2) NOT NULL,
    weighted_score DECIMAL(5, 2) NOT NULL,
    comments TEXT,
    evaluated_by UUID REFERENCES users(id),
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(criteria_id, quotation_id)
);

CREATE TABLE tbe_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tbe_id UUID REFERENCES tbe_evaluations(id) ON DELETE CASCADE,
    quotation_id UUID REFERENCES quotations(id) ON DELETE CASCADE,
    vendor_id UUID REFERENCES vendors(id),
    price_score DECIMAL(5, 2),
    quality_score DECIMAL(5, 2),
    delivery_score DECIMAL(5, 2),
    compliance_score DECIMAL(5, 2),
    total_weighted_score DECIMAL(5, 2),
    rank INTEGER,
    is_recommended BOOLEAN DEFAULT FALSE,
    remarks TEXT,
    UNIQUE(tbe_id, quotation_id)
);

-- ============================================
-- 9. PURCHASE ORDERS
-- ============================================

CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_number VARCHAR(50) UNIQUE NOT NULL,
    revision INTEGER DEFAULT 0,
    quotation_id UUID REFERENCES quotations(id),
    rfq_id UUID REFERENCES rfqs(id),
    project_id UUID REFERENCES projects(id),
    vendor_id UUID REFERENCES vendors(id) NOT NULL,
    department_id UUID REFERENCES departments(id),
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'draft',
    po_date DATE DEFAULT CURRENT_DATE,
    delivery_date DATE,
    currency VARCHAR(3) DEFAULT 'USD',
    exchange_rate DECIMAL(15, 6) DEFAULT 1,
    subtotal DECIMAL(15, 2),
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    tax_percent DECIMAL(5, 2) DEFAULT 0,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_cost DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2),
    amount_paid DECIMAL(15, 2) DEFAULT 0,
    payment_terms VARCHAR(255),
    payment_method VARCHAR(100),
    delivery_terms VARCHAR(255),
    delivery_address TEXT,
    shipping_method VARCHAR(100),
    warranty_terms TEXT,
    terms_and_conditions TEXT,
    notes TEXT,
    internal_notes TEXT,
    attachments JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_po_number ON purchase_orders(po_number);
CREATE INDEX idx_po_vendor ON purchase_orders(vendor_id);
CREATE INDEX idx_po_project ON purchase_orders(project_id);
CREATE INDEX idx_po_status ON purchase_orders(status);

CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    purchase_order_id UUID REFERENCES purchase_orders(id) ON DELETE CASCADE,
    item_id UUID REFERENCES items(id),
    quotation_item_id UUID REFERENCES quotation_items(id),
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    specifications TEXT,
    quantity DECIMAL(15, 3) NOT NULL,
    unit_id UUID REFERENCES units_of_measure(id),
    unit_price DECIMAL(15, 4) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    tax_percent DECIMAL(5, 2) DEFAULT 0,
    total_price DECIMAL(15, 2) NOT NULL,
    quantity_received DECIMAL(15, 3) DEFAULT 0,
    quantity_invoiced DECIMAL(15, 3) DEFAULT 0,
    delivery_date DATE,
    status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_po_items_po ON purchase_order_items(purchase_order_id);

-- ============================================
-- 10. GOODS RECEIPT / DELIVERY
-- ============================================

CREATE TABLE goods_receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    purchase_order_id UUID REFERENCES purchase_orders(id),
    vendor_id UUID REFERENCES vendors(id),
    received_by UUID REFERENCES users(id),
    receipt_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'pending',
    delivery_note_number VARCHAR(100),
    carrier VARCHAR(255),
    tracking_number VARCHAR(255),
    warehouse_location VARCHAR(255),
    notes TEXT,
    attachments JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gr_po ON goods_receipts(purchase_order_id);

CREATE TABLE goods_receipt_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    goods_receipt_id UUID REFERENCES goods_receipts(id) ON DELETE CASCADE,
    po_item_id UUID REFERENCES purchase_order_items(id),
    description TEXT NOT NULL,
    quantity_ordered DECIMAL(15, 3) NOT NULL,
    quantity_received DECIMAL(15, 3) NOT NULL,
    quantity_accepted DECIMAL(15, 3) NOT NULL,
    quantity_rejected DECIMAL(15, 3) DEFAULT 0,
    rejection_reason TEXT,
    condition VARCHAR(50) DEFAULT 'good',
    batch_number VARCHAR(100),
    serial_numbers TEXT[],
    expiry_date DATE,
    storage_location VARCHAR(255),
    inspection_status VARCHAR(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 11. INVOICES
-- ============================================

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    vendor_invoice_number VARCHAR(100),
    purchase_order_id UUID REFERENCES purchase_orders(id),
    goods_receipt_id UUID REFERENCES goods_receipts(id),
    vendor_id UUID REFERENCES vendors(id),
    project_id UUID REFERENCES projects(id),
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    invoice_date DATE NOT NULL,
    due_date DATE,
    currency VARCHAR(3) DEFAULT 'USD',
    subtotal DECIMAL(15, 2),
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2),
    amount_paid DECIMAL(15, 2) DEFAULT 0,
    payment_reference VARCHAR(255),
    payment_date DATE,
    payment_method VARCHAR(100),
    bank_details JSONB,
    notes TEXT,
    attachments JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoices_po ON invoices(purchase_order_id);
CREATE INDEX idx_invoices_vendor ON invoices(vendor_id);
CREATE INDEX idx_invoices_status ON invoices(status);

CREATE TABLE invoice_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    po_item_id UUID REFERENCES purchase_order_items(id),
    description TEXT NOT NULL,
    quantity DECIMAL(15, 3) NOT NULL,
    unit_price DECIMAL(15, 4) NOT NULL,
    tax_percent DECIMAL(5, 2) DEFAULT 0,
    total_price DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 12. CONTRACTS
-- ============================================

CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contract_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    vendor_id UUID REFERENCES vendors(id),
    project_id UUID REFERENCES projects(id),
    contract_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'draft',
    start_date DATE,
    end_date DATE,
    value DECIMAL(15, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    payment_terms TEXT,
    terms_and_conditions TEXT,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    signed_date DATE,
    attachments JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contracts_vendor ON contracts(vendor_id);
CREATE INDEX idx_contracts_status ON contracts(status);

-- ============================================
-- 13. APPROVALS / WORKFLOWS
-- ============================================

CREATE TABLE approval_workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    entity_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE approval_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES approval_workflows(id) ON DELETE CASCADE,
    level_number INTEGER NOT NULL,
    approver_role VARCHAR(50),
    approver_id UUID REFERENCES users(id),
    min_amount DECIMAL(15, 2),
    max_amount DECIMAL(15, 2),
    is_required BOOLEAN DEFAULT TRUE
);

CREATE TABLE approval_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES approval_workflows(id),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    current_level INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending',
    requested_by UUID REFERENCES users(id),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

CREATE TABLE approval_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES approval_requests(id) ON DELETE CASCADE,
    level_number INTEGER NOT NULL,
    approver_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    comments TEXT,
    acted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 14. AUDIT TRAIL
-- ============================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- ============================================
-- 15. NOTIFICATIONS
-- ============================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    entity_type VARCHAR(50),
    entity_id UUID,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);

-- ============================================
-- 16. DOCUMENT MANAGEMENT
-- ============================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    entity_type VARCHAR(50),
    entity_id UUID,
    uploaded_by UUID REFERENCES users(id),
    description TEXT,
    version INTEGER DEFAULT 1,
    is_public BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_entity ON documents(entity_type, entity_id);

-- ============================================
-- 17. CURRENCY AND EXCHANGE RATES
-- ============================================

CREATE TABLE currencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE exchange_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_currency VARCHAR(3) NOT NULL,
    to_currency VARCHAR(3) NOT NULL,
    rate DECIMAL(15, 6) NOT NULL,
    effective_date DATE NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_currency, to_currency, effective_date)
);

-- ============================================
-- 18. BUDGET MANAGEMENT
-- ============================================

CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    department_id UUID REFERENCES departments(id),
    fiscal_year INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    allocated_amount DECIMAL(15, 2) DEFAULT 0,
    spent_amount DECIMAL(15, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE budget_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_id UUID REFERENCES budgets(id) ON DELETE CASCADE,
    category VARCHAR(255) NOT NULL,
    allocated_amount DECIMAL(15, 2) NOT NULL,
    spent_amount DECIMAL(15, 2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 19. REPORTS AND ANALYTICS
-- ============================================

CREATE TABLE saved_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    parameters JSONB DEFAULT '{}',
    is_scheduled BOOLEAN DEFAULT FALSE,
    schedule_cron VARCHAR(100),
    last_run TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE report_exports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID REFERENCES saved_reports(id),
    user_id UUID REFERENCES users(id),
    format VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- 20. VENDOR PERFORMANCE
-- ============================================

CREATE TABLE vendor_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_orders INTEGER DEFAULT 0,
    on_time_deliveries INTEGER DEFAULT 0,
    late_deliveries INTEGER DEFAULT 0,
    total_order_value DECIMAL(15, 2) DEFAULT 0,
    quality_score DECIMAL(5, 2),
    delivery_score DECIMAL(5, 2),
    price_score DECIMAL(5, 2),
    overall_score DECIMAL(5, 2),
    notes TEXT,
    evaluated_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vendor_performance ON vendor_performance(vendor_id, period_start);

-- ============================================
-- 21. SETTINGS AND CONFIGURATIONS
-- ============================================

CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE number_sequences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) UNIQUE NOT NULL,
    prefix VARCHAR(20) NOT NULL,
    suffix VARCHAR(20),
    current_number INTEGER DEFAULT 0,
    padding INTEGER DEFAULT 5,
    reset_annually BOOLEAN DEFAULT TRUE,
    last_reset DATE
);

-- ============================================
-- 22. TAGS AND CATEGORIES
-- ============================================

CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    color VARCHAR(20),
    entity_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, entity_type)
);

CREATE TABLE entity_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tag_id, entity_type, entity_id)
);

-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert default units of measure
INSERT INTO units_of_measure (code, name, description) VALUES
    ('EA', 'Each', 'Individual unit'),
    ('PC', 'Piece', 'Single piece'),
    ('SET', 'Set', 'Complete set'),
    ('KG', 'Kilogram', 'Weight in kilograms'),
    ('LB', 'Pound', 'Weight in pounds'),
    ('M', 'Meter', 'Length in meters'),
    ('FT', 'Feet', 'Length in feet'),
    ('L', 'Liter', 'Volume in liters'),
    ('GAL', 'Gallon', 'Volume in gallons'),
    ('BOX', 'Box', 'Boxed quantity'),
    ('PKG', 'Package', 'Packaged quantity'),
    ('ROLL', 'Roll', 'Roll quantity'),
    ('SQM', 'Square Meter', 'Area in square meters'),
    ('SQF', 'Square Feet', 'Area in square feet'),
    ('HR', 'Hour', 'Time in hours'),
    ('DAY', 'Day', 'Time in days'),
    ('LOT', 'Lot', 'Complete lot');

-- Insert default currencies
INSERT INTO currencies (code, name, symbol) VALUES
    ('USD', 'US Dollar', '$'),
    ('EUR', 'Euro', '€'),
    ('GBP', 'British Pound', '£'),
    ('AED', 'UAE Dirham', 'د.إ'),
    ('SAR', 'Saudi Riyal', '﷼'),
    ('INR', 'Indian Rupee', '₹'),
    ('CNY', 'Chinese Yuan', '¥'),
    ('JPY', 'Japanese Yen', '¥');

-- Insert default number sequences
INSERT INTO number_sequences (entity_type, prefix, padding) VALUES
    ('rfq', 'RFQ-', 6),
    ('quotation', 'QT-', 6),
    ('purchase_order', 'PO-', 6),
    ('goods_receipt', 'GR-', 6),
    ('invoice', 'INV-', 6),
    ('contract', 'CON-', 6),
    ('vendor', 'VND-', 5),
    ('project', 'PRJ-', 5),
    ('tbe', 'TBE-', 6);

-- Insert default user roles
INSERT INTO user_roles (name, description, permissions) VALUES
    ('admin', 'System Administrator', '["all"]'),
    ('procurement_manager', 'Procurement Manager', '["rfq:*", "po:*", "vendor:*", "tbe:*", "reports:read"]'),
    ('procurement_officer', 'Procurement Officer', '["rfq:read", "rfq:create", "po:read", "vendor:read", "tbe:read"]'),
    ('finance', 'Finance Department', '["invoice:*", "po:read", "reports:read", "budget:*"]'),
    ('project_manager', 'Project Manager', '["project:*", "rfq:read", "po:read", "reports:read"]'),
    ('viewer', 'Read-only User', '["*:read"]');

-- Insert default system settings
INSERT INTO system_settings (key, value, description, is_public) VALUES
    ('company_name', 'Procure-Pro-ISO', 'Company/Organization Name', TRUE),
    ('default_currency', 'USD', 'Default currency for transactions', TRUE),
    ('rfq_validity_days', '30', 'Default RFQ validity period in days', TRUE),
    ('po_approval_threshold', '10000', 'PO amount requiring additional approval', FALSE),
    ('tbe_weight_price', '0.40', 'Default TBE price weight', TRUE),
    ('tbe_weight_quality', '0.25', 'Default TBE quality weight', TRUE),
    ('tbe_weight_delivery', '0.20', 'Default TBE delivery weight', TRUE),
    ('tbe_weight_compliance', '0.15', 'Default TBE compliance weight', TRUE);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update trigger to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vendors_updated_at BEFORE UPDATE ON vendors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_items_updated_at BEFORE UPDATE ON items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rfqs_updated_at BEFORE UPDATE ON rfqs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quotations_updated_at BEFORE UPDATE ON quotations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tbe_evaluations_updated_at BEFORE UPDATE ON tbe_evaluations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_purchase_orders_updated_at BEFORE UPDATE ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_goods_receipts_updated_at BEFORE UPDATE ON goods_receipts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate sequential numbers
CREATE OR REPLACE FUNCTION generate_sequence_number(p_entity_type VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    v_prefix VARCHAR;
    v_suffix VARCHAR;
    v_current INTEGER;
    v_padding INTEGER;
    v_result VARCHAR;
BEGIN
    -- Get sequence configuration
    SELECT prefix, suffix, current_number + 1, padding
    INTO v_prefix, v_suffix, v_current, v_padding
    FROM number_sequences
    WHERE entity_type = p_entity_type
    FOR UPDATE;

    -- Update the current number
    UPDATE number_sequences
    SET current_number = v_current
    WHERE entity_type = p_entity_type;

    -- Build the result
    v_result := v_prefix || LPAD(v_current::TEXT, v_padding, '0');
    IF v_suffix IS NOT NULL THEN
        v_result := v_result || v_suffix;
    END IF;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS
-- ============================================

-- RFQ Summary View
CREATE OR REPLACE VIEW v_rfq_summary AS
SELECT
    r.id,
    r.rfq_number,
    r.title,
    r.status,
    r.issue_date,
    r.closing_date,
    r.currency,
    r.estimated_value,
    p.project_number,
    p.name as project_name,
    u.first_name || ' ' || u.last_name as requested_by_name,
    COUNT(DISTINCT ri.id) as item_count,
    COUNT(DISTINCT rv.vendor_id) as vendor_count,
    COUNT(DISTINCT q.id) as quotation_count
FROM rfqs r
LEFT JOIN projects p ON r.project_id = p.id
LEFT JOIN users u ON r.requested_by = u.id
LEFT JOIN rfq_items ri ON r.id = ri.rfq_id
LEFT JOIN rfq_vendors rv ON r.id = rv.rfq_id
LEFT JOIN quotations q ON r.id = q.rfq_id
GROUP BY r.id, p.project_number, p.name, u.first_name, u.last_name;

-- Purchase Order Summary View
CREATE OR REPLACE VIEW v_po_summary AS
SELECT
    po.id,
    po.po_number,
    po.status,
    po.po_date,
    po.delivery_date,
    po.currency,
    po.total_amount,
    po.amount_paid,
    v.company_name as vendor_name,
    p.project_number,
    p.name as project_name,
    COUNT(DISTINCT poi.id) as item_count,
    SUM(poi.quantity_received) as total_received
FROM purchase_orders po
LEFT JOIN vendors v ON po.vendor_id = v.id
LEFT JOIN projects p ON po.project_id = p.id
LEFT JOIN purchase_order_items poi ON po.id = poi.purchase_order_id
GROUP BY po.id, v.company_name, p.project_number, p.name;

-- Vendor Performance Summary View
CREATE OR REPLACE VIEW v_vendor_summary AS
SELECT
    v.id,
    v.vendor_code,
    v.company_name,
    v.email,
    v.is_approved,
    v.rating,
    COUNT(DISTINCT po.id) as total_orders,
    SUM(po.total_amount) as total_order_value,
    AVG(vp.overall_score) as avg_performance_score
FROM vendors v
LEFT JOIN purchase_orders po ON v.id = po.vendor_id
LEFT JOIN vendor_performance vp ON v.id = vp.vendor_id
GROUP BY v.id;

-- ============================================
-- END OF SCHEMA
-- ============================================
