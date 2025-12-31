-- ============================================================================
-- Procure-Pro-ISO Seed Data
-- Initial setup data for development and demonstration
-- ============================================================================

-- ============================================================================
-- 1. ORGANIZATIONS
-- ============================================================================

INSERT INTO organizations (id, name, code, type, iso_certifications, address, country, phone, email, website)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Procure Pro Industries', 'PPI', 'manufacturer',
     ARRAY['ISO 9001:2015', 'ISO 17025:2017', 'IATF 16949:2016'],
     '1234 Industrial Parkway, Suite 100', 'United States', '+1-555-123-4567',
     'info@procurepro.com', 'https://procurepro.com'),

    ('22222222-2222-2222-2222-222222222222', 'Quality Testing Labs', 'QTL', 'laboratory',
     ARRAY['ISO 17025:2017', 'ISO 9001:2015'],
     '456 Science Drive', 'United States', '+1-555-234-5678',
     'contact@qualitytestlabs.com', 'https://qualitytestlabs.com'),

    ('33333333-3333-3333-3333-333333333333', 'Global Precision Instruments', 'GPI', 'supplier',
     ARRAY['ISO 9001:2015'],
     '789 Tech Boulevard', 'Germany', '+49-30-1234567',
     'sales@gpi-instruments.de', 'https://gpi-instruments.de')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 2. USERS
-- ============================================================================

-- Password hash is for 'password123' - CHANGE IN PRODUCTION
INSERT INTO users (id, organization_id, email, password_hash, first_name, last_name, role, department)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111',
     'admin@procurepro.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.n5OaD8jMTBJ.Xe6',
     'System', 'Administrator', 'admin', 'IT'),

    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111',
     'procurement@procurepro.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.n5OaD8jMTBJ.Xe6',
     'John', 'Procurement', 'procurement_manager', 'Procurement'),

    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '11111111-1111-1111-1111-111111111111',
     'quality@procurepro.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.n5OaD8jMTBJ.Xe6',
     'Jane', 'Quality', 'quality_manager', 'Quality Assurance'),

    ('dddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111',
     'engineer@procurepro.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.n5OaD8jMTBJ.Xe6',
     'Bob', 'Engineer', 'engineer', 'Engineering'),

    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '22222222-2222-2222-2222-222222222222',
     'lab@qualitytestlabs.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X.n5OaD8jMTBJ.Xe6',
     'Lab', 'Technician', 'engineer', 'Laboratory')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 3. CATEGORIES (Hierarchical)
-- ============================================================================

INSERT INTO categories (id, parent_id, code, name, description, level, path)
VALUES
    -- Level 1 Categories
    ('10000000-0000-0000-0000-000000000001', NULL, 'LAB', 'Laboratory Equipment', 'Laboratory and testing equipment', 1, '/LAB'),
    ('10000000-0000-0000-0000-000000000002', NULL, 'CAL', 'Calibration Equipment', 'Calibration and measurement instruments', 1, '/CAL'),
    ('10000000-0000-0000-0000-000000000003', NULL, 'MFG', 'Manufacturing Equipment', 'Production and manufacturing machinery', 1, '/MFG'),
    ('10000000-0000-0000-0000-000000000004', NULL, 'QC', 'Quality Control', 'Quality control and inspection equipment', 1, '/QC'),
    ('10000000-0000-0000-0000-000000000005', NULL, 'IT', 'IT Equipment', 'Information technology hardware and software', 1, '/IT'),
    ('10000000-0000-0000-0000-000000000006', NULL, 'CONS', 'Consumables', 'Laboratory and office consumables', 1, '/CONS'),
    ('10000000-0000-0000-0000-000000000007', NULL, 'SVC', 'Services', 'Professional and technical services', 1, '/SVC'),

    -- Level 2 - Laboratory Equipment Subcategories
    ('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'LAB-ANL', 'Analytical Instruments', 'Spectrometers, chromatographs, etc.', 2, '/LAB/LAB-ANL'),
    ('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 'LAB-PREP', 'Sample Preparation', 'Sample preparation equipment', 2, '/LAB/LAB-PREP'),
    ('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001', 'LAB-ENV', 'Environmental Testing', 'Chambers, ovens, climate control', 2, '/LAB/LAB-ENV'),

    -- Level 2 - Calibration Equipment Subcategories
    ('20000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', 'CAL-DIM', 'Dimensional Calibration', 'Gauges, blocks, micrometers', 2, '/CAL/CAL-DIM'),
    ('20000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000002', 'CAL-ELEC', 'Electrical Calibration', 'Multimeters, oscilloscopes', 2, '/CAL/CAL-ELEC'),
    ('20000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000002', 'CAL-TEMP', 'Temperature Calibration', 'Thermometers, probes, baths', 2, '/CAL/CAL-TEMP'),

    -- Level 2 - Quality Control Subcategories
    ('20000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000004', 'QC-INSP', 'Inspection Equipment', 'CMM, vision systems', 2, '/QC/QC-INSP'),
    ('20000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000004', 'QC-NDT', 'NDT Equipment', 'Non-destructive testing', 2, '/QC/QC-NDT')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 4. VENDORS
-- ============================================================================

INSERT INTO vendors (id, vendor_code, name, legal_name, category, status, rating, iso_certified, certifications,
    primary_contact_name, primary_contact_email, primary_contact_phone, address, country, payment_terms, currency)
VALUES
    ('40000000-0000-0000-0000-000000000001', 'VND-001', 'Precision Instruments Co.',
     'Precision Instruments Corporation', 'Laboratory Equipment', 'approved', 4.5, true,
     '{"certifications": ["ISO 9001:2015", "ISO 17025:2017"]}',
     'Michael Chen', 'mchen@precisioninst.com', '+1-555-111-2222',
     '100 Innovation Way, San Jose, CA 95134', 'United States', 'Net 30', 'USD'),

    ('40000000-0000-0000-0000-000000000002', 'VND-002', 'MetroTech GmbH',
     'MetroTech Measurement Technologies GmbH', 'Calibration Equipment', 'approved', 4.8, true,
     '{"certifications": ["ISO 9001:2015", "ISO 17025:2017", "DKD Accreditation"]}',
     'Hans Mueller', 'h.mueller@metrotech.de', '+49-89-123456',
     'Industriestrasse 45, 80939 Munich', 'Germany', 'Net 45', 'EUR'),

    ('40000000-0000-0000-0000-000000000003', 'VND-003', 'ThermoScan Industries',
     'ThermoScan Industries Ltd.', 'Environmental Testing', 'approved', 4.2, true,
     '{"certifications": ["ISO 9001:2015"]}',
     'Sarah Johnson', 'sjohnson@thermoscan.com', '+1-555-333-4444',
     '500 Temperature Lane, Austin, TX 78701', 'United States', 'Net 30', 'USD'),

    ('40000000-0000-0000-0000-000000000004', 'VND-004', 'Quality Parts Supply',
     'Quality Parts Supply Inc.', 'Consumables', 'conditionally_approved', 3.8, false,
     '{"certifications": ["ISO 9001:2015"]}',
     'David Lee', 'dlee@qualityparts.com', '+1-555-555-6666',
     '200 Parts Avenue, Chicago, IL 60601', 'United States', 'Net 15', 'USD'),

    ('40000000-0000-0000-0000-000000000005', 'VND-005', 'Calibration Services Ltd.',
     'Calibration Services Limited', 'Services', 'approved', 4.7, true,
     '{"certifications": ["ISO 17025:2017", "UKAS Accreditation"]}',
     'Emma Wilson', 'ewilson@calservices.co.uk', '+44-20-12345678',
     '10 Measurement Street, London EC1A 1BB', 'United Kingdom', 'Net 30', 'GBP'),

    ('40000000-0000-0000-0000-000000000006', 'VND-006', 'Asia Pacific Electronics',
     'Asia Pacific Electronics Pte Ltd', 'IT Equipment', 'pending', NULL, false,
     '{"certifications": []}',
     'Wei Zhang', 'wzhang@apelectronics.sg', '+65-6789-0123',
     '88 Tech Park Drive, Singapore 123456', 'Singapore', 'Net 30', 'SGD')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 5. PRODUCTS
-- ============================================================================

INSERT INTO products (id, category_id, product_code, name, description, manufacturer, model,
    specifications, unit_of_measure, standard_lead_time, is_calibration_required, calibration_interval)
VALUES
    ('50000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001',
     'PROD-SPEC-001', 'UV-Vis Spectrophotometer', 'Double-beam UV-Visible spectrophotometer for analytical applications',
     'Precision Instruments Co.', 'UV-2600i',
     '{"wavelength_range": "190-1100 nm", "resolution": "0.1 nm", "accuracy": "±0.3 nm", "stray_light": "<0.02%"}',
     'Unit', 45, true, 365),

    ('50000000-0000-0000-0000-000000000002', '20000000-0000-0000-0000-000000000004',
     'PROD-GAUGE-001', 'Precision Gauge Block Set', 'Grade 0 gauge block set per ISO 3650',
     'MetroTech GmbH', 'GB-103',
     '{"grade": "0", "material": "Steel", "pieces": 103, "range": "0.5-100 mm"}',
     'Set', 21, true, 365),

    ('50000000-0000-0000-0000-000000000003', '20000000-0000-0000-0000-000000000003',
     'PROD-CHAMBER-001', 'Environmental Test Chamber', 'Temperature and humidity environmental test chamber',
     'ThermoScan Industries', 'ETC-500',
     '{"temp_range": "-40 to +150°C", "humidity_range": "20-95% RH", "volume": "500L", "uniformity": "±0.5°C"}',
     'Unit', 60, true, 180),

    ('50000000-0000-0000-0000-000000000004', '20000000-0000-0000-0000-000000000005',
     'PROD-DMM-001', 'Digital Multimeter 6.5 Digit', 'High-precision 6.5 digit digital multimeter',
     'MetroTech GmbH', 'DMM-6500',
     '{"digits": "6.5", "dc_accuracy": "0.0035%", "ac_accuracy": "0.06%", "resistance_range": "100Ω to 100MΩ"}',
     'Unit', 14, true, 365),

    ('50000000-0000-0000-0000-000000000005', '20000000-0000-0000-0000-000000000007',
     'PROD-CMM-001', 'Coordinate Measuring Machine', '3-axis bridge-type CMM for precision measurements',
     'Precision Instruments Co.', 'CMM-BRIDGE-850',
     '{"measuring_range": "800x500x400 mm", "resolution": "0.1 µm", "mpee": "1.5 + L/350 µm"}',
     'Unit', 90, true, 365),

    ('50000000-0000-0000-0000-000000000006', '20000000-0000-0000-0000-000000000006',
     'PROD-TEMP-001', 'Reference Temperature Probe', 'SPRT reference thermometer for calibration',
     'Calibration Services Ltd.', 'SPRT-25',
     '{"range": "-200 to +660°C", "uncertainty": "±0.001°C", "type": "Standard Platinum Resistance Thermometer"}',
     'Unit', 30, true, 365)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 6. VENDOR EVALUATIONS (Sample)
-- ============================================================================

INSERT INTO vendor_evaluations (id, vendor_id, evaluation_date, evaluator_id, evaluation_type,
    quality_score, delivery_score, price_score, service_score, compliance_score, overall_score, recommendation)
VALUES
    ('60000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001',
     '2024-01-15', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'periodic',
     4.5, 4.0, 4.0, 4.5, 5.0, 4.4, 'approve'),

    ('60000000-0000-0000-0000-000000000002', '40000000-0000-0000-0000-000000000002',
     '2024-02-20', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'periodic',
     5.0, 4.5, 3.5, 5.0, 5.0, 4.6, 'approve'),

    ('60000000-0000-0000-0000-000000000003', '40000000-0000-0000-0000-000000000004',
     '2024-03-10', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'initial',
     3.5, 4.0, 4.5, 3.5, 3.5, 3.8, 'conditional')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 7. SAMPLE RFQ
-- ============================================================================

INSERT INTO rfqs (id, rfq_number, title, description, category_id, status, rfq_type,
    issue_date, closing_date, delivery_required_by, currency, estimated_value, created_by)
VALUES
    ('70000000-0000-0000-0000-000000000001', 'RFQ-2024-001',
     'Laboratory Spectrophotometer Procurement',
     'Request for quotation for UV-Vis spectrophotometer with calibration services',
     '20000000-0000-0000-0000-000000000001', 'published', 'open',
     '2024-06-01', '2024-06-30 17:00:00+00', '2024-08-15', 'USD', 75000.00,
     'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),

    ('70000000-0000-0000-0000-000000000002', 'RFQ-2024-002',
     'Calibration Equipment Upgrade',
     'Procurement of precision gauge blocks and digital multimeters',
     '10000000-0000-0000-0000-000000000002', 'draft', 'limited',
     NULL, NULL, '2024-09-30', 'USD', 45000.00,
     'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb')
ON CONFLICT DO NOTHING;

-- RFQ Line Items
INSERT INTO rfq_items (id, rfq_id, product_id, line_number, description, quantity, unit_of_measure)
VALUES
    ('71000000-0000-0000-0000-000000000001', '70000000-0000-0000-0000-000000000001',
     '50000000-0000-0000-0000-000000000001', 1, 'UV-Vis Spectrophotometer UV-2600i or equivalent', 2, 'Unit'),

    ('71000000-0000-0000-0000-000000000002', '70000000-0000-0000-0000-000000000001',
     NULL, 2, 'Installation and training services', 1, 'Service'),

    ('71000000-0000-0000-0000-000000000003', '70000000-0000-0000-0000-000000000002',
     '50000000-0000-0000-0000-000000000002', 1, 'Precision Gauge Block Set Grade 0', 3, 'Set'),

    ('71000000-0000-0000-0000-000000000004', '70000000-0000-0000-0000-000000000002',
     '50000000-0000-0000-0000-000000000004', 2, 'Digital Multimeter 6.5 Digit', 5, 'Unit')
ON CONFLICT DO NOTHING;

-- RFQ Invitations
INSERT INTO rfq_invitations (rfq_id, vendor_id, invited_by, response_status)
VALUES
    ('70000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000001',
     'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'accepted'),

    ('70000000-0000-0000-0000-000000000001', '40000000-0000-0000-0000-000000000002',
     'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'pending')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 8. DOCUMENT CONTROL TEMPLATES
-- ============================================================================

INSERT INTO document_control (id, document_number, title, document_type, version, status,
    category, description, iso_reference, author_id)
VALUES
    ('80000000-0000-0000-0000-000000000001', 'DOC-QMS-001',
     'Quality Management System Manual', 'manual', '2.0', 'approved',
     'Quality', 'Main QMS manual per ISO 9001:2015', 'ISO 9001:2015',
     'cccccccc-cccc-cccc-cccc-cccccccccccc'),

    ('80000000-0000-0000-0000-000000000002', 'DOC-PROC-001',
     'Procurement Procedure', 'procedure', '1.5', 'approved',
     'Procurement', 'Standard operating procedure for procurement activities', 'ISO 9001:2015 Clause 8.4',
     'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),

    ('80000000-0000-0000-0000-000000000003', 'DOC-PROC-002',
     'Vendor Qualification Procedure', 'procedure', '1.2', 'approved',
     'Procurement', 'Procedure for vendor evaluation and approval', 'ISO 9001:2015 Clause 8.4.1',
     'cccccccc-cccc-cccc-cccc-cccccccccccc'),

    ('80000000-0000-0000-0000-000000000004', 'DOC-FORM-001',
     'Purchase Requisition Form', 'form', '1.0', 'approved',
     'Procurement', 'Standard form for purchase requisitions', NULL,
     'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),

    ('80000000-0000-0000-0000-000000000005', 'DOC-FORM-002',
     'FAT/SAT Protocol Template', 'template', '1.1', 'approved',
     'Quality', 'Template for factory and site acceptance testing', 'ISO 17025:2017',
     'cccccccc-cccc-cccc-cccc-cccccccccccc')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 9. NOTIFICATION TEMPLATES
-- ============================================================================

INSERT INTO notifications (user_id, title, message, notification_type, priority, entity_type, entity_id)
VALUES
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Welcome to Procure-Pro-ISO',
     'Your account has been set up. Please review the system documentation to get started.',
     'system', 'normal', NULL, NULL),

    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'RFQ-2024-001 Published',
     'RFQ for Laboratory Spectrophotometer Procurement has been published and invitations sent.',
     'rfq', 'high', 'rfqs', '70000000-0000-0000-0000-000000000001'),

    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Vendor Evaluation Due',
     'Annual evaluation for Precision Instruments Co. is due in 30 days.',
     'vendor', 'normal', 'vendors', '40000000-0000-0000-0000-000000000001')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 10. UPDATE SCHEMA VERSION
-- ============================================================================

INSERT INTO schema_version (version, description, applied_by)
VALUES ('1.0.0-seed', 'Initial seed data applied', 'seed_runner')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- END OF SEED DATA
-- ============================================================================
