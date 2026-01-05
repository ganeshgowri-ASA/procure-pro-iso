"""
Sample data for Procure-Pro-ISO Streamlit App
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Equipment Master Data
def get_equipment_data():
    return pd.DataFrame({
        'Equipment ID': ['EQ-001', 'EQ-002', 'EQ-003', 'EQ-004', 'EQ-005', 'EQ-006', 'EQ-007', 'EQ-008'],
        'Name': [
            'CNC Milling Machine', 'Coordinate Measuring Machine', 'Industrial Robot Arm',
            'Laser Cutting System', 'EDM Wire Cut Machine', 'Optical Comparator',
            'CNC Lathe', 'Surface Grinder'
        ],
        'Category': ['Manufacturing', 'Quality', 'Automation', 'Manufacturing', 'Manufacturing', 'Quality', 'Manufacturing', 'Manufacturing'],
        'Manufacturer': ['HAAS', 'Zeiss', 'FANUC', 'TRUMPF', 'Mitsubishi', 'Nikon', 'Mazak', 'Okamoto'],
        'Model': ['VF-2SS', 'CONTURA G3', 'M-20iD/25', 'TruLaser 3030', 'MV2400R', 'V-24B', 'QT-250MY', 'ACC-820DX'],
        'Specifications': [
            '5-axis, 12000 RPM, 30HP spindle',
            'Accuracy: 1.8+L/300 μm',
            '25kg payload, 1831mm reach',
            '6kW fiber laser, 3m x 1.5m bed',
            'Wire diameter: 0.1-0.3mm',
            '600mm screen, 100x magnification',
            'Multi-axis turning center',
            '800mm x 400mm table'
        ],
        'Quantity': [2, 1, 4, 1, 2, 1, 3, 2],
        'Unit Price': [89500, 125000, 45000, 320000, 78000, 35000, 95000, 42000],
        'Total Price': [179000, 125000, 180000, 320000, 156000, 35000, 285000, 84000],
        'Status': ['Active', 'Ordered', 'Pending', 'Active', 'Delivered', 'Active', 'Active', 'Pending'],
        'RFQ Status': ['Completed', 'Completed', 'Assigned', 'Pending', 'Completed', 'Assigned', 'Completed', 'Pending']
    })

# RFQ Data
def get_rfq_data():
    return pd.DataFrame({
        'RFQ Number': ['RFQ-2024-001', 'RFQ-2024-002', 'RFQ-2024-003', 'RFQ-2024-004', 'RFQ-2024-005'],
        'Title': [
            'CNC Machinery Procurement', 'Quality Control Equipment', 'Automation Systems',
            'Laser Cutting System', 'EDM Equipment Package'
        ],
        'Description': [
            'Procurement of CNC milling machines and lathes for production expansion',
            'CMM and optical measurement systems for QC department',
            'Industrial robot arms and automation components',
            'High-power fiber laser cutting system',
            'Wire cut and sinker EDM machines'
        ],
        'Status': ['Open', 'Closed', 'Open', 'Draft', 'Awarded'],
        'Priority': ['High', 'Normal', 'Critical', 'High', 'Normal'],
        'Issue Date': ['2024-01-15', '2024-01-10', '2024-01-20', '2024-01-25', '2024-01-05'],
        'Closing Date': ['2024-02-15', '2024-02-01', '2024-02-20', '2024-02-25', '2024-01-25'],
        'Estimated Value': [450000, 180000, 280000, 350000, 200000],
        'Vendors Invited': [5, 4, 6, 0, 4],
        'Responses': [3, 4, 2, 0, 4]
    })

# Vendor Data
def get_vendor_data():
    return pd.DataFrame({
        'Vendor Code': ['V-001', 'V-002', 'V-003', 'V-004', 'V-005', 'V-006', 'V-007'],
        'Company Name': [
            'Precision Machinery Co.', 'TechParts International', 'AutomaTech Solutions',
            'QualityFirst Instruments', 'GlobalTools Ltd', 'Swiss Precision AG', 'NewVendor Systems'
        ],
        'Contact Person': ['John Smith', 'Maria Garcia', 'Kenji Tanaka', 'Hans Mueller', 'Li Wei', 'Pierre Dubois', 'Sarah Johnson'],
        'Email': [
            'john@precisionmach.com', 'maria@techparts.com', 'kenji@automatech.jp',
            'hans@qualityfirst.de', 'liwei@globaltools.cn', 'pierre@swissprecision.ch', 'sarah@newvendor.com'
        ],
        'Country': ['USA', 'Germany', 'Japan', 'Germany', 'China', 'Switzerland', 'USA'],
        'Category': [
            'Manufacturing Equipment', 'Precision Components', 'Automation',
            'Quality Control', 'Tooling & Fixtures', 'High-Precision Components', 'General Supplies'
        ],
        'Rating': [4.8, 4.5, 4.9, 4.7, 4.2, 5.0, 0.0],
        'Status': ['Approved', 'Approved', 'Approved', 'Approved', 'Approved', 'Approved', 'Pending'],
        'Certifications': [
            'ISO 9001, ISO 14001', 'ISO 9001, IATF 16949', 'ISO 9001, ISO 17025',
            'ISO 9001, ISO 17025, DAkkS', 'ISO 9001', 'ISO 9001, ISO 13485, AS9100', ''
        ],
        'Total Orders': [24, 18, 12, 15, 32, 8, 0],
        'Total Value': [1250000, 890000, 720000, 560000, 420000, 380000, 0],
        'On-Time Delivery %': [96, 92, 99, 94, 88, 100, 0],
        'Quality Score %': [98, 95, 99, 97, 90, 100, 0]
    })

# Technical Evaluation Data
def get_technical_evaluation_data():
    vendors = ['Precision Machinery Co.', 'TechParts International', 'AutomaTech Solutions']

    scores = pd.DataFrame({
        'Vendor': vendors,
        'Overall Score': [90.2, 88.7, 88.1],
        'Technical Score': [92, 90, 89],
        'Quality Score': [95, 88, 91],
        'Delivery Score': [88, 87, 85],
        'Compliance Score': [86, 90, 88],
        'Recommendation': ['Recommended', 'Recommended', 'Acceptable']
    })

    ctq_matrix = pd.DataFrame({
        'Parameter': [
            'Spindle Speed (RPM)', 'Positioning Accuracy', 'Tool Capacity',
            'Work Area (XYZ)', 'Spindle Power', 'ISO Certification',
            'Warranty Period', 'Training Included'
        ],
        'Weight %': [15, 20, 10, 15, 12, 10, 8, 10],
        'Requirement': [
            '≥ 12,000 RPM', '≤ 0.005mm', '≥ 24 tools',
            '≥ 1000x500x500mm', '≥ 30HP', 'ISO 9001 Required',
            '≥ 2 years', 'Full operator training'
        ],
        'Precision Machinery': ['12,000 ✓', '0.003mm ✓', '30 tools ✓', '1016x508x508mm ✓', '30HP ✓', 'ISO 9001:2015 ✓', '3 years ✓', '5 days on-site ✓'],
        'TechParts Intl': ['10,000 ✗', '0.004mm ✓', '24 tools ✓', '1200x600x600mm ✓', '35HP ✓', 'ISO 9001:2015 ✓', '2 years ✓', '3 days on-site ✓'],
        'AutomaTech': ['15,000 ✓', '0.005mm ✓', '20 tools ✗', '1000x500x500mm ✓', '25HP ✗', 'ISO 9001:2015 ✓', '2 years ✓', '2 days remote ✗']
    })

    return scores, ctq_matrix

# Commercial Evaluation Data
def get_commercial_evaluation_data():
    pricing = pd.DataFrame({
        'Vendor': ['Precision Machinery Co.', 'TechParts International', 'AutomaTech Solutions'],
        'Unit Price': [89500, 92000, 87000],
        'Quantity': [2, 2, 2],
        'Subtotal': [179000, 184000, 174000],
        'Discount %': [5, 8, 3],
        'Tax %': [8, 8, 8],
        'Shipping': [4500, 6200, 8500],
        'Total': [185775, 189152, 190810],
        'Payment Terms': ['Net 30', 'Net 45', 'Net 30'],
        'Delivery Days': [45, 60, 90],
        'Warranty': ['3 years', '2 years', '2 years']
    })

    tco = pd.DataFrame({
        'Cost Category': [
            'Initial Purchase', 'Installation', 'Training',
            'Annual Maintenance (5yr)', 'Extended Warranty', 'Spare Parts (Est.)', 'Total 5-Year TCO'
        ],
        'Precision Machinery': [185775, 12000, 0, 45000, 0, 18000, 260775],
        'TechParts Intl': [189152, 15000, 5000, 52000, 12000, 22000, 295152],
        'AutomaTech': [190810, 18000, 8000, 48000, 15000, 20000, 299810]
    })

    return pricing, tco

# Budget Trend Data
def get_budget_trend_data():
    months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']
    return pd.DataFrame({
        'Month': months,
        'Budget': [1200000, 1350000, 1500000, 1650000, 1750000, 1800000],
        'Spent': [980000, 1150000, 1380000, 1520000, 1680000, 1420000]
    })

# Recent Activity
def get_recent_activity():
    return [
        {'type': 'rfq', 'message': 'RFQ-2024-003 received 2 new responses', 'time': '2 hours ago'},
        {'type': 'approval', 'message': 'PO-2024-012 approved by Finance', 'time': '4 hours ago'},
        {'type': 'vendor', 'message': 'New vendor registration: NewVendor Systems', 'time': '6 hours ago'},
        {'type': 'equipment', 'message': 'CMM System marked as delivered', 'time': '1 day ago'},
        {'type': 'evaluation', 'message': 'TBE completed for RFQ-2024-001', 'time': '2 days ago'}
    ]
