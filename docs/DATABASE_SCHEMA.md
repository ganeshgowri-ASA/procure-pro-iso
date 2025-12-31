# Procure-Pro-ISO Database Schema

## Overview

The database uses PostgreSQL with 22+ tables designed to support a comprehensive procurement management system with ISO compliance features.

---

## Entity Relationship Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Users     │────<│  Projects    │>────│ Departments  │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                     │
                            │                     │
                     ┌──────┴──────┐              │
                     ▼             ▼              ▼
              ┌──────────┐  ┌──────────────┐  ┌──────────────┐
              │   RFQs   │  │   Budgets    │  │Organizations │
              └──────────┘  └──────────────┘  └──────────────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   ┌──────────────┐    ┌──────────────┐
   │  RFQ Items   │    │  RFQ Vendors │
   └──────────────┘    └──────────────┘
          │                   │
          └─────────┬─────────┘
                    ▼
             ┌──────────────┐
             │  Quotations  │──────>┌──────────┐
             └──────────────┘       │  Vendors │
                    │               └──────────┘
                    ▼
         ┌─────────────────────┐
         │   TBE Evaluations   │
         └─────────────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │   Purchase Orders   │
         └─────────────────────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   ┌──────────────┐    ┌──────────────┐
   │Goods Receipts│    │   Invoices   │
   └──────────────┘    └──────────────┘
```

---

## Core Tables

### 1. Users & Authentication

#### users
Primary user accounts for system access.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | Primary key |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| first_name | VARCHAR(100) | NOT NULL | First name |
| last_name | VARCHAR(100) | NOT NULL | Last name |
| phone | VARCHAR(20) | | Phone number |
| department | VARCHAR(100) | | Department name |
| role | VARCHAR(50) | NOT NULL, DEFAULT 'user' | User role |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| last_login | TIMESTAMP WITH TIME ZONE | | Last login time |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP | |
| updated_at | TIMESTAMP WITH TIME ZONE | | |

#### user_roles
Role definitions with permissions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(50) | Role name (admin, procurement_manager, etc.) |
| description | TEXT | Role description |
| permissions | JSONB | Array of permission strings |

---

### 2. Organizations & Departments

#### organizations
Company/organization records.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Organization name |
| code | VARCHAR(50) | Unique code |
| address | TEXT | Full address |
| city | VARCHAR(100) | City |
| country | VARCHAR(100) | Country |
| phone | VARCHAR(50) | Phone |
| email | VARCHAR(255) | Email |
| website | VARCHAR(255) | Website URL |
| is_active | BOOLEAN | Active status |

#### departments
Department records within organizations.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| organization_id | UUID | FK to organizations |
| name | VARCHAR(255) | Department name |
| code | VARCHAR(50) | Department code |
| manager_id | UUID | FK to users |
| budget_limit | DECIMAL(15,2) | Budget limit |

---

### 3. Projects

#### projects
Project management records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| project_number | VARCHAR(50) | UNIQUE, NOT NULL | Auto-generated number |
| name | VARCHAR(255) | NOT NULL | Project name |
| description | TEXT | | Project description |
| client_name | VARCHAR(255) | | Client/customer name |
| organization_id | UUID | FK | Organization |
| department_id | UUID | FK | Department |
| project_manager_id | UUID | FK | Project manager |
| status | VARCHAR(50) | DEFAULT 'active' | active, on_hold, completed, cancelled |
| start_date | DATE | | Project start |
| end_date | DATE | | Project end |
| budget | DECIMAL(15,2) | | Total budget |
| currency | VARCHAR(3) | DEFAULT 'USD' | Currency code |
| location | VARCHAR(255) | | Project location |
| is_iso_compliant | BOOLEAN | DEFAULT TRUE | ISO compliance flag |
| metadata | JSONB | DEFAULT '{}' | Additional data |

---

### 4. Vendors

#### vendors
Supplier/vendor master records.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| vendor_code | VARCHAR(50) | Unique vendor code |
| company_name | VARCHAR(255) | Company name |
| trade_name | VARCHAR(255) | Trade/brand name |
| contact_person | VARCHAR(255) | Primary contact |
| email | VARCHAR(255) | Email address |
| phone | VARCHAR(50) | Phone number |
| address | TEXT | Full address |
| city | VARCHAR(100) | City |
| country | VARCHAR(100) | Country |
| website | VARCHAR(255) | Website |
| tax_id | VARCHAR(50) | Tax identification |
| bank_name | VARCHAR(255) | Bank name |
| bank_account | VARCHAR(100) | Account number |
| payment_terms | VARCHAR(100) | Default payment terms |
| credit_limit | DECIMAL(15,2) | Credit limit |
| rating | DECIMAL(3,2) | Performance rating (0-5) |
| vendor_type | VARCHAR(50) | Vendor classification |
| categories | TEXT[] | Product categories |
| certifications | TEXT[] | Certifications held |
| is_approved | BOOLEAN | Approved vendor flag |
| is_blacklisted | BOOLEAN | Blacklist flag |

---

### 5. Items

#### items
Material/product master records.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| item_code | VARCHAR(100) | Unique item code |
| name | VARCHAR(255) | Item name |
| description | TEXT | Full description |
| specifications | TEXT | Technical specs |
| category_id | UUID | FK to item_categories |
| unit_id | UUID | FK to units_of_measure |
| brand | VARCHAR(100) | Brand name |
| model | VARCHAR(100) | Model number |
| manufacturer | VARCHAR(255) | Manufacturer |
| part_number | VARCHAR(100) | Part number |
| hs_code | VARCHAR(20) | HS tariff code |
| standard_price | DECIMAL(15,2) | Standard unit price |
| lead_time_days | INTEGER | Standard lead time |

---

### 6. RFQs

#### rfqs
Request for Quotation header.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| rfq_number | VARCHAR(50) | Unique RFQ number |
| title | VARCHAR(255) | RFQ title |
| description | TEXT | RFQ description |
| project_id | UUID | FK to projects |
| requested_by | UUID | FK to users |
| approved_by | UUID | FK to users |
| status | VARCHAR(50) | draft, open, closed, cancelled |
| rfq_type | VARCHAR(50) | standard, urgent, framework |
| priority | VARCHAR(20) | low, normal, high, critical |
| issue_date | DATE | Issue date |
| closing_date | DATE | Submission deadline |
| validity_days | INTEGER | Quote validity period |
| delivery_location | VARCHAR(255) | Delivery address |
| currency | VARCHAR(3) | Currency code |
| estimated_value | DECIMAL(15,2) | Estimated total value |
| terms_and_conditions | TEXT | T&C |
| attachments | JSONB | Attached files |

#### rfq_items
RFQ line items.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| rfq_id | UUID | FK to rfqs |
| item_id | UUID | FK to items (optional) |
| line_number | INTEGER | Sequence number |
| description | TEXT | Item description |
| specifications | TEXT | Technical specs |
| quantity | DECIMAL(15,3) | Required quantity |
| unit_id | UUID | FK to units_of_measure |
| target_price | DECIMAL(15,2) | Target/budget price |
| required_delivery_date | DATE | Required date |

---

### 7. Quotations

#### quotations
Vendor quotation header.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| quotation_number | VARCHAR(50) | Unique quote number |
| rfq_id | UUID | FK to rfqs |
| vendor_id | UUID | FK to vendors |
| status | VARCHAR(50) | submitted, under_review, accepted, rejected |
| submission_date | TIMESTAMP | Submission timestamp |
| validity_date | DATE | Quote expiry date |
| subtotal | DECIMAL(15,2) | Subtotal before discounts |
| discount_percent | DECIMAL(5,2) | Discount percentage |
| tax_percent | DECIMAL(5,2) | Tax percentage |
| total_amount | DECIMAL(15,2) | Final total |
| payment_terms | VARCHAR(255) | Payment terms |
| delivery_terms | VARCHAR(255) | Delivery terms |
| delivery_days | INTEGER | Lead time in days |
| is_technically_compliant | BOOLEAN | Technical compliance |
| technical_score | DECIMAL(5,2) | Technical score |
| commercial_score | DECIMAL(5,2) | Commercial score |
| overall_score | DECIMAL(5,2) | Weighted total score |
| rank | INTEGER | Ranking position |
| is_selected | BOOLEAN | Selected for award |

---

### 8. TBE (Technical Bid Evaluation)

#### tbe_evaluations
TBE evaluation header.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| evaluation_number | VARCHAR(50) | Unique TBE number |
| rfq_id | UUID | FK to rfqs |
| title | VARCHAR(255) | Evaluation title |
| status | VARCHAR(50) | draft, in_progress, completed, approved |
| weight_price | DECIMAL(5,2) | Price weight (default 0.40) |
| weight_quality | DECIMAL(5,2) | Quality weight (default 0.25) |
| weight_delivery | DECIMAL(5,2) | Delivery weight (default 0.20) |
| weight_compliance | DECIMAL(5,2) | Compliance weight (default 0.15) |
| recommendation | TEXT | Final recommendation |
| selected_vendor_id | UUID | FK to vendors |

#### tbe_criteria
Evaluation criteria definitions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tbe_id | UUID | FK to tbe_evaluations |
| criteria_name | VARCHAR(255) | Criteria name |
| category | VARCHAR(50) | price, quality, delivery, compliance |
| weight | DECIMAL(5,2) | Criteria weight |
| max_score | DECIMAL(5,2) | Maximum score |

#### tbe_scores
Individual scores per quotation per criteria.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tbe_id | UUID | FK to tbe_evaluations |
| criteria_id | UUID | FK to tbe_criteria |
| quotation_id | UUID | FK to quotations |
| score | DECIMAL(5,2) | Raw score |
| weighted_score | DECIMAL(5,2) | Weighted score |
| comments | TEXT | Evaluator comments |

---

### 9. Purchase Orders

#### purchase_orders
Purchase order header.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| po_number | VARCHAR(50) | Unique PO number |
| revision | INTEGER | Revision number |
| quotation_id | UUID | FK to quotations |
| vendor_id | UUID | FK to vendors |
| project_id | UUID | FK to projects |
| status | VARCHAR(50) | draft, pending_approval, approved, sent, acknowledged, completed, cancelled |
| po_date | DATE | PO date |
| delivery_date | DATE | Expected delivery |
| subtotal | DECIMAL(15,2) | Subtotal |
| discount_amount | DECIMAL(15,2) | Discount amount |
| tax_amount | DECIMAL(15,2) | Tax amount |
| shipping_cost | DECIMAL(15,2) | Shipping cost |
| total_amount | DECIMAL(15,2) | Total PO value |
| amount_paid | DECIMAL(15,2) | Amount paid so far |
| payment_terms | VARCHAR(255) | Payment terms |
| delivery_terms | VARCHAR(255) | Delivery terms |
| delivery_address | TEXT | Delivery address |

---

### 10. Goods Receipts & Invoices

#### goods_receipts
Material receipt records.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| receipt_number | VARCHAR(50) | Receipt number |
| purchase_order_id | UUID | FK to purchase_orders |
| vendor_id | UUID | FK to vendors |
| received_by | UUID | FK to users |
| receipt_date | DATE | Receipt date |
| status | VARCHAR(50) | pending, partial, complete |
| delivery_note_number | VARCHAR(100) | Vendor's delivery note |

#### invoices
Vendor invoice records.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| invoice_number | VARCHAR(50) | Internal invoice number |
| vendor_invoice_number | VARCHAR(100) | Vendor's invoice number |
| purchase_order_id | UUID | FK to purchase_orders |
| goods_receipt_id | UUID | FK to goods_receipts |
| vendor_id | UUID | FK to vendors |
| status | VARCHAR(50) | pending, verified, approved, paid |
| invoice_date | DATE | Invoice date |
| due_date | DATE | Payment due date |
| total_amount | DECIMAL(15,2) | Invoice total |
| amount_paid | DECIMAL(15,2) | Amount paid |
| payment_date | DATE | Payment date |

---

## Supporting Tables

### Audit & Logging

#### audit_logs
Tracks all data changes for compliance.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | User who made change |
| action | VARCHAR(50) | create, update, delete |
| entity_type | VARCHAR(50) | Table name |
| entity_id | UUID | Record ID |
| old_values | JSONB | Previous values |
| new_values | JSONB | New values |
| ip_address | INET | Client IP |
| created_at | TIMESTAMP | Timestamp |

### Reference Data

#### currencies
Currency codes and names.

#### units_of_measure
Standard units (EA, KG, M, etc.)

#### number_sequences
Auto-numbering configuration for RFQs, POs, etc.

---

## Indexes

Key indexes for performance:

```sql
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_rfqs_status ON rfqs(status);
CREATE INDEX idx_rfqs_project ON rfqs(project_id);
CREATE INDEX idx_quotations_rfq ON quotations(rfq_id);
CREATE INDEX idx_quotations_vendor ON quotations(vendor_id);
CREATE INDEX idx_po_vendor ON purchase_orders(vendor_id);
CREATE INDEX idx_po_status ON purchase_orders(status);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
```

---

## Functions

### generate_sequence_number(entity_type)
Generates sequential numbers for RFQs, POs, etc.

### update_updated_at_column()
Trigger function to auto-update `updated_at` timestamps.
