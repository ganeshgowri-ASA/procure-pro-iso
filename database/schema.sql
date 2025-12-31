-- ============================================================================
-- Procure-Pro-ISO Database Schema
-- ISO-compliant Procurement Lifecycle Management System
-- Supports: ISO 17025, ISO 9001, IATF 16949 Standards
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. ORGANIZATION & USER MANAGEMENT
-- ============================================================================

-- Table 1: Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('manufacturer', 'laboratory', 'supplier', 'customer')),
    iso_certifications TEXT[], -- Array of ISO certifications
    address TEXT,
    country VARCHAR(100),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    tax_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'procurement_manager', 'quality_manager', 'engineer', 'approver', 'viewer')),
    department VARCHAR(100),
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: User Permissions
CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, permission, resource_type, resource_id)
);

-- ============================================================================
-- 2. VENDOR MANAGEMENT
-- ============================================================================

-- Table 4: Vendors
CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
    vendor_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    category VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'conditionally_approved', 'suspended', 'blacklisted')),
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    iso_certified BOOLEAN DEFAULT FALSE,
    certifications JSONB DEFAULT '[]'::jsonb,
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    primary_contact_phone VARCHAR(50),
    address TEXT,
    country VARCHAR(100),
    payment_terms VARCHAR(100),
    currency VARCHAR(10) DEFAULT 'USD',
    tax_id VARCHAR(100),
    bank_details JSONB,
    notes TEXT,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 5: Vendor Evaluations
CREATE TABLE IF NOT EXISTS vendor_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    evaluation_date DATE NOT NULL,
    evaluator_id UUID REFERENCES users(id),
    evaluation_type VARCHAR(50) NOT NULL CHECK (evaluation_type IN ('initial', 'periodic', 'special', 'audit')),
    quality_score DECIMAL(5,2),
    delivery_score DECIMAL(5,2),
    price_score DECIMAL(5,2),
    service_score DECIMAL(5,2),
    compliance_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    recommendation VARCHAR(50) CHECK (recommendation IN ('approve', 'conditional', 'reject', 'suspend')),
    findings TEXT,
    corrective_actions TEXT,
    next_evaluation_date DATE,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 6: Vendor Documents
CREATE TABLE IF NOT EXISTS vendor_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size INTEGER,
    mime_type VARCHAR(100),
    expiry_date DATE,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. PRODUCT & CATEGORY MANAGEMENT
-- ============================================================================

-- Table 7: Categories
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    level INTEGER DEFAULT 1,
    path VARCHAR(500), -- Materialized path for hierarchy
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 8: Products/Equipment
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    product_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    specifications JSONB DEFAULT '{}'::jsonb,
    unit_of_measure VARCHAR(50),
    standard_lead_time INTEGER, -- Days
    minimum_order_quantity DECIMAL(15,4),
    is_calibration_required BOOLEAN DEFAULT FALSE,
    calibration_interval INTEGER, -- Days
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 9: Technical Specifications Templates
CREATE TABLE IF NOT EXISTS technical_specifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    specification_name VARCHAR(255) NOT NULL,
    specification_type VARCHAR(50) NOT NULL,
    unit VARCHAR(50),
    min_value DECIMAL(15,6),
    max_value DECIMAL(15,6),
    nominal_value DECIMAL(15,6),
    tolerance DECIMAL(15,6),
    is_critical BOOLEAN DEFAULT FALSE,
    test_method VARCHAR(255),
    iso_reference VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. RFQ (REQUEST FOR QUOTATION) MANAGEMENT
-- ============================================================================

-- Table 10: RFQs
CREATE TABLE IF NOT EXISTS rfqs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfq_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES categories(id),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'evaluation', 'awarded', 'cancelled', 'closed')),
    rfq_type VARCHAR(50) DEFAULT 'open' CHECK (rfq_type IN ('open', 'limited', 'single_source')),
    issue_date DATE,
    closing_date TIMESTAMP WITH TIME ZONE,
    delivery_required_by DATE,
    delivery_location TEXT,
    payment_terms VARCHAR(255),
    currency VARCHAR(10) DEFAULT 'USD',
    estimated_value DECIMAL(15,2),
    evaluation_criteria JSONB DEFAULT '[]'::jsonb,
    terms_and_conditions TEXT,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 11: RFQ Line Items
CREATE TABLE IF NOT EXISTS rfq_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfq_id UUID REFERENCES rfqs(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(15,4) NOT NULL,
    unit_of_measure VARCHAR(50),
    technical_requirements JSONB DEFAULT '{}'::jsonb,
    delivery_schedule JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(rfq_id, line_number)
);

-- Table 12: RFQ Invitations
CREATE TABLE IF NOT EXISTS rfq_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfq_id UUID REFERENCES rfqs(id) ON DELETE CASCADE,
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    invited_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    invited_by UUID REFERENCES users(id),
    response_status VARCHAR(50) DEFAULT 'pending' CHECK (response_status IN ('pending', 'accepted', 'declined', 'no_response')),
    response_date TIMESTAMP WITH TIME ZONE,
    UNIQUE(rfq_id, vendor_id)
);

-- ============================================================================
-- 5. QUOTATION & TBE (TECHNICAL BID EVALUATION)
-- ============================================================================

-- Table 13: Quotations
CREATE TABLE IF NOT EXISTS quotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rfq_id UUID REFERENCES rfqs(id) ON DELETE CASCADE,
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    quotation_number VARCHAR(100),
    submission_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    validity_date DATE,
    total_amount DECIMAL(15,2),
    currency VARCHAR(10) DEFAULT 'USD',
    delivery_terms VARCHAR(255),
    payment_terms VARCHAR(255),
    warranty_terms TEXT,
    technical_compliance JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'submitted' CHECK (status IN ('submitted', 'under_review', 'technically_approved', 'technically_rejected', 'awarded', 'rejected')),
    notes TEXT,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(rfq_id, vendor_id)
);

-- Table 14: Quotation Line Items
CREATE TABLE IF NOT EXISTS quotation_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES quotations(id) ON DELETE CASCADE,
    rfq_item_id UUID REFERENCES rfq_items(id),
    line_number INTEGER NOT NULL,
    description TEXT,
    quantity DECIMAL(15,4),
    unit_price DECIMAL(15,4),
    total_price DECIMAL(15,2),
    lead_time INTEGER, -- Days
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    specifications_offered JSONB DEFAULT '{}'::jsonb,
    deviations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 15: Technical Bid Evaluations (TBE)
CREATE TABLE IF NOT EXISTS technical_bid_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quotation_id UUID REFERENCES quotations(id) ON DELETE CASCADE,
    evaluator_id UUID REFERENCES users(id),
    evaluation_date DATE NOT NULL,
    technical_score DECIMAL(5,2),
    compliance_score DECIMAL(5,2),
    quality_score DECIMAL(5,2),
    experience_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    is_technically_acceptable BOOLEAN,
    evaluation_matrix JSONB DEFAULT '{}'::jsonb,
    strengths TEXT,
    weaknesses TEXT,
    clarifications_required TEXT,
    recommendation VARCHAR(50) CHECK (recommendation IN ('approve', 'approve_with_conditions', 'reject', 'needs_clarification')),
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 6. PURCHASE ORDER MANAGEMENT
-- ============================================================================

-- Table 16: Purchase Orders
CREATE TABLE IF NOT EXISTS purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_number VARCHAR(50) UNIQUE NOT NULL,
    quotation_id UUID REFERENCES quotations(id),
    vendor_id UUID REFERENCES vendors(id),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'sent', 'acknowledged', 'in_progress', 'partially_delivered', 'completed', 'cancelled')),
    order_date DATE,
    delivery_date DATE,
    delivery_address TEXT,
    shipping_method VARCHAR(100),
    incoterms VARCHAR(50),
    currency VARCHAR(10) DEFAULT 'USD',
    subtotal DECIMAL(15,2),
    tax_amount DECIMAL(15,2),
    shipping_amount DECIMAL(15,2),
    discount_amount DECIMAL(15,2),
    total_amount DECIMAL(15,2),
    payment_terms VARCHAR(255),
    terms_and_conditions TEXT,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 17: Purchase Order Items
CREATE TABLE IF NOT EXISTS purchase_order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    purchase_order_id UUID REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quotation_item_id UUID REFERENCES quotation_items(id),
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity DECIMAL(15,4) NOT NULL,
    unit_of_measure VARCHAR(50),
    unit_price DECIMAL(15,4) NOT NULL,
    total_price DECIMAL(15,2) NOT NULL,
    delivery_date DATE,
    received_quantity DECIMAL(15,4) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'partially_received', 'received', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 7. GOODS RECEIPT & INSPECTION
-- ============================================================================

-- Table 18: Goods Receipts
CREATE TABLE IF NOT EXISTS goods_receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    purchase_order_id UUID REFERENCES purchase_orders(id),
    vendor_id UUID REFERENCES vendors(id),
    receipt_date DATE NOT NULL,
    delivery_note_number VARCHAR(100),
    carrier VARCHAR(255),
    received_by UUID REFERENCES users(id),
    warehouse_location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'received' CHECK (status IN ('received', 'under_inspection', 'accepted', 'partially_accepted', 'rejected')),
    notes TEXT,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 19: Goods Receipt Items
CREATE TABLE IF NOT EXISTS goods_receipt_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    goods_receipt_id UUID REFERENCES goods_receipts(id) ON DELETE CASCADE,
    po_item_id UUID REFERENCES purchase_order_items(id),
    product_id UUID REFERENCES products(id),
    quantity_received DECIMAL(15,4) NOT NULL,
    quantity_accepted DECIMAL(15,4),
    quantity_rejected DECIMAL(15,4),
    batch_number VARCHAR(100),
    serial_numbers TEXT[],
    inspection_status VARCHAR(50) DEFAULT 'pending' CHECK (inspection_status IN ('pending', 'in_progress', 'passed', 'failed', 'conditional')),
    rejection_reason TEXT,
    storage_location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 8. FAT/SAT (FACTORY/SITE ACCEPTANCE TESTING)
-- ============================================================================

-- Table 20: Acceptance Tests
CREATE TABLE IF NOT EXISTS acceptance_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_number VARCHAR(50) UNIQUE NOT NULL,
    purchase_order_id UUID REFERENCES purchase_orders(id),
    product_id UUID REFERENCES products(id),
    test_type VARCHAR(10) NOT NULL CHECK (test_type IN ('FAT', 'SAT', 'IQ', 'OQ', 'PQ')),
    status VARCHAR(50) DEFAULT 'planned' CHECK (status IN ('planned', 'scheduled', 'in_progress', 'passed', 'failed', 'conditional_pass', 'cancelled')),
    planned_date DATE,
    actual_date DATE,
    location VARCHAR(255),
    test_protocol_id UUID,
    test_protocol_version VARCHAR(50),
    lead_tester UUID REFERENCES users(id),
    witness_required BOOLEAN DEFAULT FALSE,
    witness_name VARCHAR(255),
    overall_result VARCHAR(50),
    deviations_found INTEGER DEFAULT 0,
    critical_deviations INTEGER DEFAULT 0,
    test_report_path VARCHAR(500),
    certificates JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 21: Acceptance Test Results
CREATE TABLE IF NOT EXISTS acceptance_test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    acceptance_test_id UUID REFERENCES acceptance_tests(id) ON DELETE CASCADE,
    test_step INTEGER NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    test_procedure TEXT,
    acceptance_criteria TEXT,
    expected_result TEXT,
    actual_result TEXT,
    result_status VARCHAR(20) CHECK (result_status IN ('pass', 'fail', 'N/A', 'deviation')),
    measurement_value DECIMAL(15,6),
    measurement_unit VARCHAR(50),
    deviation_description TEXT,
    corrective_action TEXT,
    tested_by UUID REFERENCES users(id),
    tested_at TIMESTAMP WITH TIME ZONE,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 9. ASSET & EQUIPMENT MANAGEMENT
-- ============================================================================

-- Table 22: Assets/Equipment
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_number VARCHAR(100) UNIQUE NOT NULL,
    product_id UUID REFERENCES products(id),
    purchase_order_id UUID REFERENCES purchase_orders(id),
    goods_receipt_id UUID REFERENCES goods_receipts(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    serial_number VARCHAR(255),
    manufacturer VARCHAR(255),
    model VARCHAR(255),
    category_id UUID REFERENCES categories(id),
    location VARCHAR(255),
    department VARCHAR(100),
    custodian_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'under_maintenance', 'calibration_due', 'retired', 'disposed')),
    acquisition_date DATE,
    acquisition_cost DECIMAL(15,2),
    warranty_expiry DATE,
    expected_life_years INTEGER,
    depreciation_method VARCHAR(50),
    current_value DECIMAL(15,2),
    is_calibrated BOOLEAN DEFAULT FALSE,
    last_calibration_date DATE,
    next_calibration_date DATE,
    calibration_interval INTEGER, -- Days
    maintenance_schedule JSONB,
    specifications JSONB DEFAULT '{}'::jsonb,
    documents JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 23: Asset Calibration Records
CREATE TABLE IF NOT EXISTS asset_calibrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    calibration_number VARCHAR(100) UNIQUE NOT NULL,
    calibration_date DATE NOT NULL,
    calibration_due_date DATE NOT NULL,
    calibration_type VARCHAR(50) CHECK (calibration_type IN ('initial', 'periodic', 'after_repair', 'verification')),
    performed_by VARCHAR(255),
    calibration_provider VARCHAR(255),
    certificate_number VARCHAR(100),
    certificate_path VARCHAR(500),
    status VARCHAR(50) CHECK (status IN ('passed', 'failed', 'adjusted', 'out_of_tolerance')),
    temperature DECIMAL(6,2),
    humidity DECIMAL(5,2),
    results JSONB DEFAULT '{}'::jsonb,
    deviations TEXT,
    notes TEXT,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 24: Asset Maintenance Records
CREATE TABLE IF NOT EXISTS asset_maintenance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    maintenance_number VARCHAR(100) UNIQUE NOT NULL,
    maintenance_type VARCHAR(50) CHECK (maintenance_type IN ('preventive', 'corrective', 'emergency', 'inspection')),
    scheduled_date DATE,
    actual_date DATE,
    status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'overdue')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    work_performed TEXT,
    parts_used JSONB DEFAULT '[]'::jsonb,
    labor_hours DECIMAL(8,2),
    cost DECIMAL(15,2),
    performed_by UUID REFERENCES users(id),
    vendor_id UUID REFERENCES vendors(id),
    next_maintenance_date DATE,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 10. AUDIT & COMPLIANCE TRACKING
-- ============================================================================

-- Table 25: Audit Trail
CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 26: Document Control
CREATE TABLE IF NOT EXISTS document_control (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_number VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'pending_review', 'approved', 'obsolete', 'superseded')),
    category VARCHAR(100),
    description TEXT,
    file_path VARCHAR(500),
    file_size INTEGER,
    mime_type VARCHAR(100),
    iso_reference VARCHAR(100),
    effective_date DATE,
    review_date DATE,
    expiry_date DATE,
    author_id UUID REFERENCES users(id),
    reviewer_id UUID REFERENCES users(id),
    approver_id UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    revision_history JSONB DEFAULT '[]'::jsonb,
    access_control JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 27: Non-Conformance Reports
CREATE TABLE IF NOT EXISTS non_conformance_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ncr_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    ncr_type VARCHAR(50) CHECK (ncr_type IN ('product', 'process', 'system', 'supplier', 'customer')),
    severity VARCHAR(20) CHECK (severity IN ('minor', 'major', 'critical')),
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'under_investigation', 'pending_action', 'closed', 'verified')),
    source VARCHAR(100),
    detected_date DATE NOT NULL,
    detected_by UUID REFERENCES users(id),
    affected_entity_type VARCHAR(100),
    affected_entity_id UUID,
    root_cause TEXT,
    immediate_action TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    target_closure_date DATE,
    actual_closure_date DATE,
    cost_impact DECIMAL(15,2),
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 11. NOTIFICATIONS & WORKFLOWS
-- ============================================================================

-- Table 28: Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    entity_type VARCHAR(100),
    entity_id UUID,
    action_url VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    is_email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 29: Approval Workflows
CREATE TABLE IF NOT EXISTS approval_workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'approved', 'rejected', 'cancelled')),
    initiated_by UUID REFERENCES users(id),
    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    workflow_definition JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 30: Approval Steps
CREATE TABLE IF NOT EXISTS approval_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES approval_workflows(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    approver_id UUID REFERENCES users(id),
    approver_role VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'skipped')),
    decision_date TIMESTAMP WITH TIME ZONE,
    comments TEXT,
    delegation_to UUID REFERENCES users(id),
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Organizations
CREATE INDEX IF NOT EXISTS idx_organizations_code ON organizations(code);
CREATE INDEX IF NOT EXISTS idx_organizations_type ON organizations(type);

-- Users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Vendors
CREATE INDEX IF NOT EXISTS idx_vendors_code ON vendors(vendor_code);
CREATE INDEX IF NOT EXISTS idx_vendors_status ON vendors(status);
CREATE INDEX IF NOT EXISTS idx_vendors_category ON vendors(category);

-- Categories
CREATE INDEX IF NOT EXISTS idx_categories_code ON categories(code);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_path ON categories(path);

-- Products
CREATE INDEX IF NOT EXISTS idx_products_code ON products(product_code);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);

-- RFQs
CREATE INDEX IF NOT EXISTS idx_rfqs_number ON rfqs(rfq_number);
CREATE INDEX IF NOT EXISTS idx_rfqs_status ON rfqs(status);
CREATE INDEX IF NOT EXISTS idx_rfqs_closing_date ON rfqs(closing_date);

-- Purchase Orders
CREATE INDEX IF NOT EXISTS idx_po_number ON purchase_orders(po_number);
CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_po_vendor ON purchase_orders(vendor_id);

-- Assets
CREATE INDEX IF NOT EXISTS idx_assets_number ON assets(asset_number);
CREATE INDEX IF NOT EXISTS idx_assets_serial ON assets(serial_number);
CREATE INDEX IF NOT EXISTS idx_assets_status ON assets(status);
CREATE INDEX IF NOT EXISTS idx_assets_calibration_due ON assets(next_calibration_date);

-- Acceptance Tests
CREATE INDEX IF NOT EXISTS idx_acceptance_tests_number ON acceptance_tests(test_number);
CREATE INDEX IF NOT EXISTS idx_acceptance_tests_type ON acceptance_tests(test_type);
CREATE INDEX IF NOT EXISTS idx_acceptance_tests_status ON acceptance_tests(status);

-- Audit Trail
CREATE INDEX IF NOT EXISTS idx_audit_trail_user ON audit_trail(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_entity ON audit_trail(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_created ON audit_trail(created_at);

-- Notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(user_id, is_read);

-- NCRs
CREATE INDEX IF NOT EXISTS idx_ncr_number ON non_conformance_reports(ncr_number);
CREATE INDEX IF NOT EXISTS idx_ncr_status ON non_conformance_reports(status);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to all relevant tables
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT table_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND column_name = 'updated_at'
        AND table_name NOT IN ('audit_trail')
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%I_updated_at ON %I;
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        ', t, t, t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to create audit trail entry
CREATE OR REPLACE FUNCTION create_audit_entry()
RETURNS TRIGGER AS $$
DECLARE
    audit_user_id UUID;
BEGIN
    -- Try to get user_id from the record if available
    IF TG_OP = 'DELETE' THEN
        IF OLD ? 'created_by' THEN
            audit_user_id := (OLD->>'created_by')::UUID;
        END IF;
    ELSE
        IF NEW ? 'created_by' THEN
            audit_user_id := (NEW->>'created_by')::UUID;
        ELSIF NEW ? 'user_id' THEN
            audit_user_id := (NEW->>'user_id')::UUID;
        END IF;
    END IF;

    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_trail (user_id, action, entity_type, entity_id, new_values)
        VALUES (audit_user_id, 'CREATE', TG_TABLE_NAME, NEW.id, to_jsonb(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_trail (user_id, action, entity_type, entity_id, old_values, new_values)
        VALUES (audit_user_id, 'UPDATE', TG_TABLE_NAME, NEW.id, to_jsonb(OLD), to_jsonb(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_trail (user_id, action, entity_type, entity_id, old_values)
        VALUES (audit_user_id, 'DELETE', TG_TABLE_NAME, OLD.id, to_jsonb(OLD));
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(255)
);

INSERT INTO schema_version (version, description, applied_by)
VALUES ('1.0.0', 'Initial schema - 30 tables for ISO-compliant procurement lifecycle', 'migration_runner')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
