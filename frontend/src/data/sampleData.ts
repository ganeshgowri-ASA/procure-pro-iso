import { Equipment, RFQ, Vendor, TechnicalEvaluation, CommercialEvaluation, KPI } from '../types';

// Dashboard KPIs
export const dashboardKPIs: KPI[] = [
  {
    title: 'Total Equipment',
    value: 12,
    change: 2,
    trend: 'up',
    color: 'blue',
    icon: 'Package'
  },
  {
    title: 'Total Budget',
    value: '$1.8M',
    change: 5.2,
    trend: 'up',
    color: 'green',
    icon: 'DollarSign'
  },
  {
    title: 'Active RFQs',
    value: 3,
    change: -1,
    trend: 'down',
    color: 'orange',
    icon: 'FileText'
  },
  {
    title: 'Pending Approvals',
    value: 4,
    change: 2,
    trend: 'up',
    color: 'purple',
    icon: 'Clock'
  }
];

// Equipment Master List
export const equipmentData: Equipment[] = [
  {
    id: '1',
    equipmentId: 'EQ-001',
    name: 'CNC Milling Machine',
    category: 'Manufacturing',
    manufacturer: 'HAAS',
    model: 'VF-2SS',
    specifications: '5-axis, 12000 RPM, 30HP spindle',
    quantity: 2,
    unitPrice: 89500,
    totalPrice: 179000,
    status: 'Active',
    rfqStatus: 'Completed',
    createdAt: '2024-01-15',
    updatedAt: '2024-01-20'
  },
  {
    id: '2',
    equipmentId: 'EQ-002',
    name: 'Coordinate Measuring Machine',
    category: 'Quality',
    manufacturer: 'Zeiss',
    model: 'CONTURA G3',
    specifications: 'Accuracy: 1.8+L/300 μm',
    quantity: 1,
    unitPrice: 125000,
    totalPrice: 125000,
    status: 'Ordered',
    rfqStatus: 'Completed',
    createdAt: '2024-01-18',
    updatedAt: '2024-01-22'
  },
  {
    id: '3',
    equipmentId: 'EQ-003',
    name: 'Industrial Robot Arm',
    category: 'Automation',
    manufacturer: 'FANUC',
    model: 'M-20iD/25',
    specifications: '25kg payload, 1831mm reach',
    quantity: 4,
    unitPrice: 45000,
    totalPrice: 180000,
    status: 'Pending',
    rfqStatus: 'Assigned',
    createdAt: '2024-01-20',
    updatedAt: '2024-01-20'
  },
  {
    id: '4',
    equipmentId: 'EQ-004',
    name: 'Laser Cutting System',
    category: 'Manufacturing',
    manufacturer: 'TRUMPF',
    model: 'TruLaser 3030',
    specifications: '6kW fiber laser, 3m x 1.5m bed',
    quantity: 1,
    unitPrice: 320000,
    totalPrice: 320000,
    status: 'Active',
    rfqStatus: 'Pending',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-25'
  },
  {
    id: '5',
    equipmentId: 'EQ-005',
    name: 'EDM Wire Cut Machine',
    category: 'Manufacturing',
    manufacturer: 'Mitsubishi',
    model: 'MV2400R',
    specifications: 'Wire diameter: 0.1-0.3mm',
    quantity: 2,
    unitPrice: 78000,
    totalPrice: 156000,
    status: 'Delivered',
    rfqStatus: 'Completed',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-28'
  },
  {
    id: '6',
    equipmentId: 'EQ-006',
    name: 'Optical Comparator',
    category: 'Quality',
    manufacturer: 'Nikon',
    model: 'V-24B',
    specifications: '600mm screen, 100x magnification',
    quantity: 1,
    unitPrice: 35000,
    totalPrice: 35000,
    status: 'Active',
    rfqStatus: 'Assigned',
    createdAt: '2024-01-12',
    updatedAt: '2024-01-15'
  },
  {
    id: '7',
    equipmentId: 'EQ-007',
    name: 'CNC Lathe',
    category: 'Manufacturing',
    manufacturer: 'Mazak',
    model: 'QT-250MY',
    specifications: 'Multi-axis turning center',
    quantity: 3,
    unitPrice: 95000,
    totalPrice: 285000,
    status: 'Active',
    rfqStatus: 'Completed',
    createdAt: '2024-01-08',
    updatedAt: '2024-01-20'
  },
  {
    id: '8',
    equipmentId: 'EQ-008',
    name: 'Surface Grinder',
    category: 'Manufacturing',
    manufacturer: 'Okamoto',
    model: 'ACC-820DX',
    specifications: '800mm x 400mm table',
    quantity: 2,
    unitPrice: 42000,
    totalPrice: 84000,
    status: 'Pending',
    rfqStatus: 'Pending',
    createdAt: '2024-01-22',
    updatedAt: '2024-01-22'
  }
];

// RFQ Data
export const rfqData: RFQ[] = [
  {
    id: '1',
    rfqNumber: 'RFQ-2024-001',
    title: 'CNC Machinery Procurement',
    description: 'Procurement of CNC milling machines and lathes for production expansion',
    status: 'Open',
    priority: 'High',
    issueDate: '2024-01-15',
    closingDate: '2024-02-15',
    estimatedValue: 450000,
    vendorsInvited: 5,
    responsesReceived: 3,
    items: [
      { id: '1', description: 'CNC Milling Machine', quantity: 2, unit: 'EA', targetPrice: 90000 },
      { id: '2', description: 'CNC Lathe', quantity: 3, unit: 'EA', targetPrice: 95000 }
    ],
    createdAt: '2024-01-15'
  },
  {
    id: '2',
    rfqNumber: 'RFQ-2024-002',
    title: 'Quality Control Equipment',
    description: 'CMM and optical measurement systems for QC department',
    status: 'Closed',
    priority: 'Normal',
    issueDate: '2024-01-10',
    closingDate: '2024-02-01',
    estimatedValue: 180000,
    vendorsInvited: 4,
    responsesReceived: 4,
    items: [
      { id: '1', description: 'CMM System', quantity: 1, unit: 'EA', targetPrice: 125000 },
      { id: '2', description: 'Optical Comparator', quantity: 1, unit: 'EA', targetPrice: 35000 }
    ],
    createdAt: '2024-01-10'
  },
  {
    id: '3',
    rfqNumber: 'RFQ-2024-003',
    title: 'Automation Systems',
    description: 'Industrial robot arms and automation components',
    status: 'Open',
    priority: 'Critical',
    issueDate: '2024-01-20',
    closingDate: '2024-02-20',
    estimatedValue: 280000,
    vendorsInvited: 6,
    responsesReceived: 2,
    items: [
      { id: '1', description: 'Industrial Robot Arm', quantity: 4, unit: 'EA', targetPrice: 45000 },
      { id: '2', description: 'Robot Controller', quantity: 4, unit: 'EA', targetPrice: 15000 }
    ],
    createdAt: '2024-01-20'
  },
  {
    id: '4',
    rfqNumber: 'RFQ-2024-004',
    title: 'Laser Cutting System',
    description: 'High-power fiber laser cutting system',
    status: 'Draft',
    priority: 'High',
    issueDate: '2024-01-25',
    closingDate: '2024-02-25',
    estimatedValue: 350000,
    vendorsInvited: 0,
    responsesReceived: 0,
    items: [
      { id: '1', description: 'Fiber Laser Cutting Machine', quantity: 1, unit: 'EA', targetPrice: 320000 }
    ],
    createdAt: '2024-01-25'
  },
  {
    id: '5',
    rfqNumber: 'RFQ-2024-005',
    title: 'EDM Equipment Package',
    description: 'Wire cut and sinker EDM machines',
    status: 'Awarded',
    priority: 'Normal',
    issueDate: '2024-01-05',
    closingDate: '2024-01-25',
    estimatedValue: 200000,
    vendorsInvited: 4,
    responsesReceived: 4,
    items: [
      { id: '1', description: 'Wire EDM Machine', quantity: 2, unit: 'EA', targetPrice: 78000 },
      { id: '2', description: 'Sinker EDM Machine', quantity: 1, unit: 'EA', targetPrice: 55000 }
    ],
    createdAt: '2024-01-05'
  }
];

// Vendor Data
export const vendorData: Vendor[] = [
  {
    id: '1',
    vendorCode: 'V-001',
    companyName: 'Precision Machinery Co.',
    contactPerson: 'John Smith',
    email: 'john@precisionmach.com',
    phone: '+1-555-0101',
    country: 'USA',
    category: 'Manufacturing Equipment',
    rating: 4.8,
    status: 'Approved',
    certifications: ['ISO 9001', 'ISO 14001'],
    totalOrders: 24,
    totalValue: 1250000,
    onTimeDelivery: 96,
    qualityScore: 98
  },
  {
    id: '2',
    vendorCode: 'V-002',
    companyName: 'TechParts International',
    contactPerson: 'Maria Garcia',
    email: 'maria@techparts.com',
    phone: '+1-555-0102',
    country: 'Germany',
    category: 'Precision Components',
    rating: 4.5,
    status: 'Approved',
    certifications: ['ISO 9001', 'IATF 16949'],
    totalOrders: 18,
    totalValue: 890000,
    onTimeDelivery: 92,
    qualityScore: 95
  },
  {
    id: '3',
    vendorCode: 'V-003',
    companyName: 'AutomaTech Solutions',
    contactPerson: 'Kenji Tanaka',
    email: 'kenji@automatech.jp',
    phone: '+81-3-5555-0103',
    country: 'Japan',
    category: 'Automation',
    rating: 4.9,
    status: 'Approved',
    certifications: ['ISO 9001', 'ISO 17025'],
    totalOrders: 12,
    totalValue: 720000,
    onTimeDelivery: 99,
    qualityScore: 99
  },
  {
    id: '4',
    vendorCode: 'V-004',
    companyName: 'QualityFirst Instruments',
    contactPerson: 'Hans Mueller',
    email: 'hans@qualityfirst.de',
    phone: '+49-30-5555-0104',
    country: 'Germany',
    category: 'Quality Control',
    rating: 4.7,
    status: 'Approved',
    certifications: ['ISO 9001', 'ISO 17025', 'DAkkS'],
    totalOrders: 15,
    totalValue: 560000,
    onTimeDelivery: 94,
    qualityScore: 97
  },
  {
    id: '5',
    vendorCode: 'V-005',
    companyName: 'GlobalTools Ltd',
    contactPerson: 'Li Wei',
    email: 'liwei@globaltools.cn',
    phone: '+86-21-5555-0105',
    country: 'China',
    category: 'Tooling & Fixtures',
    rating: 4.2,
    status: 'Approved',
    certifications: ['ISO 9001'],
    totalOrders: 32,
    totalValue: 420000,
    onTimeDelivery: 88,
    qualityScore: 90
  },
  {
    id: '6',
    vendorCode: 'V-006',
    companyName: 'Swiss Precision AG',
    contactPerson: 'Pierre Dubois',
    email: 'pierre@swissprecision.ch',
    phone: '+41-44-5555-0106',
    country: 'Switzerland',
    category: 'High-Precision Components',
    rating: 5.0,
    status: 'Approved',
    certifications: ['ISO 9001', 'ISO 13485', 'AS9100'],
    totalOrders: 8,
    totalValue: 380000,
    onTimeDelivery: 100,
    qualityScore: 100
  },
  {
    id: '7',
    vendorCode: 'V-007',
    companyName: 'NewVendor Systems',
    contactPerson: 'Sarah Johnson',
    email: 'sarah@newvendor.com',
    phone: '+1-555-0107',
    country: 'USA',
    category: 'General Supplies',
    rating: 0,
    status: 'Pending',
    certifications: [],
    totalOrders: 0,
    totalValue: 0,
    onTimeDelivery: 0,
    qualityScore: 0
  }
];

// Technical Evaluation Data
export const technicalEvaluationData: TechnicalEvaluation = {
  id: '1',
  rfqId: '1',
  rfqTitle: 'CNC Machinery Procurement',
  status: 'Completed',
  vendors: [
    {
      vendorId: '1',
      vendorName: 'Precision Machinery Co.',
      overallScore: 90.2,
      technicalScore: 92,
      qualityScore: 95,
      deliveryScore: 88,
      complianceScore: 86,
      recommendation: 'Recommended'
    },
    {
      vendorId: '2',
      vendorName: 'TechParts International',
      overallScore: 88.7,
      technicalScore: 90,
      qualityScore: 88,
      deliveryScore: 87,
      complianceScore: 90,
      recommendation: 'Recommended'
    },
    {
      vendorId: '3',
      vendorName: 'AutomaTech Solutions',
      overallScore: 88.1,
      technicalScore: 89,
      qualityScore: 91,
      deliveryScore: 85,
      complianceScore: 88,
      recommendation: 'Acceptable'
    }
  ],
  ctqMatrix: [
    {
      id: '1',
      parameter: 'Spindle Speed (RPM)',
      weight: 15,
      requirement: '≥ 12,000 RPM',
      vendors: [
        { vendorId: '1', value: '12,000', score: 100, compliant: true },
        { vendorId: '2', value: '10,000', score: 80, compliant: false },
        { vendorId: '3', value: '15,000', score: 100, compliant: true }
      ]
    },
    {
      id: '2',
      parameter: 'Positioning Accuracy',
      weight: 20,
      requirement: '≤ 0.005mm',
      vendors: [
        { vendorId: '1', value: '0.003mm', score: 100, compliant: true },
        { vendorId: '2', value: '0.004mm', score: 95, compliant: true },
        { vendorId: '3', value: '0.005mm', score: 90, compliant: true }
      ]
    },
    {
      id: '3',
      parameter: 'Tool Capacity',
      weight: 10,
      requirement: '≥ 24 tools',
      vendors: [
        { vendorId: '1', value: '30 tools', score: 100, compliant: true },
        { vendorId: '2', value: '24 tools', score: 90, compliant: true },
        { vendorId: '3', value: '20 tools', score: 75, compliant: false }
      ]
    },
    {
      id: '4',
      parameter: 'Work Area (XYZ)',
      weight: 15,
      requirement: '≥ 1000x500x500mm',
      vendors: [
        { vendorId: '1', value: '1016x508x508mm', score: 95, compliant: true },
        { vendorId: '2', value: '1200x600x600mm', score: 100, compliant: true },
        { vendorId: '3', value: '1000x500x500mm', score: 90, compliant: true }
      ]
    },
    {
      id: '5',
      parameter: 'Spindle Power',
      weight: 12,
      requirement: '≥ 30HP',
      vendors: [
        { vendorId: '1', value: '30HP', score: 90, compliant: true },
        { vendorId: '2', value: '35HP', score: 100, compliant: true },
        { vendorId: '3', value: '25HP', score: 75, compliant: false }
      ]
    },
    {
      id: '6',
      parameter: 'ISO Certification',
      weight: 10,
      requirement: 'ISO 9001 Required',
      vendors: [
        { vendorId: '1', value: 'ISO 9001:2015', score: 100, compliant: true },
        { vendorId: '2', value: 'ISO 9001:2015', score: 100, compliant: true },
        { vendorId: '3', value: 'ISO 9001:2015', score: 100, compliant: true }
      ]
    },
    {
      id: '7',
      parameter: 'Warranty Period',
      weight: 8,
      requirement: '≥ 2 years',
      vendors: [
        { vendorId: '1', value: '3 years', score: 100, compliant: true },
        { vendorId: '2', value: '2 years', score: 85, compliant: true },
        { vendorId: '3', value: '2 years', score: 85, compliant: true }
      ]
    },
    {
      id: '8',
      parameter: 'Training Included',
      weight: 10,
      requirement: 'Full operator training',
      vendors: [
        { vendorId: '1', value: '5 days on-site', score: 100, compliant: true },
        { vendorId: '2', value: '3 days on-site', score: 85, compliant: true },
        { vendorId: '3', value: '2 days remote', score: 70, compliant: false }
      ]
    }
  ],
  createdAt: '2024-01-20'
};

// Commercial Evaluation Data
export const commercialEvaluationData: CommercialEvaluation = {
  id: '1',
  rfqId: '1',
  rfqTitle: 'CNC Machinery Procurement',
  status: 'Completed',
  vendors: [
    {
      vendorId: '1',
      vendorName: 'Precision Machinery Co.',
      unitPrice: 89500,
      quantity: 2,
      subtotal: 179000,
      discount: 5,
      tax: 8,
      shipping: 4500,
      total: 185775,
      paymentTerms: 'Net 30',
      deliveryDays: 45,
      warranty: '3 years'
    },
    {
      vendorId: '2',
      vendorName: 'TechParts International',
      unitPrice: 92000,
      quantity: 2,
      subtotal: 184000,
      discount: 8,
      tax: 8,
      shipping: 6200,
      total: 189152,
      paymentTerms: 'Net 45',
      deliveryDays: 60,
      warranty: '2 years'
    },
    {
      vendorId: '3',
      vendorName: 'AutomaTech Solutions',
      unitPrice: 87000,
      quantity: 2,
      subtotal: 174000,
      discount: 3,
      tax: 8,
      shipping: 8500,
      total: 190810,
      paymentTerms: 'Net 30',
      deliveryDays: 90,
      warranty: '2 years'
    }
  ],
  tcoComparison: [
    {
      category: 'Initial Purchase',
      vendors: [
        { vendorId: '1', amount: 185775 },
        { vendorId: '2', amount: 189152 },
        { vendorId: '3', amount: 190810 }
      ]
    },
    {
      category: 'Installation',
      vendors: [
        { vendorId: '1', amount: 12000 },
        { vendorId: '2', amount: 15000 },
        { vendorId: '3', amount: 18000 }
      ]
    },
    {
      category: 'Training',
      vendors: [
        { vendorId: '1', amount: 0 },
        { vendorId: '2', amount: 5000 },
        { vendorId: '3', amount: 8000 }
      ]
    },
    {
      category: 'Annual Maintenance (5yr)',
      vendors: [
        { vendorId: '1', amount: 45000 },
        { vendorId: '2', amount: 52000 },
        { vendorId: '3', amount: 48000 }
      ]
    },
    {
      category: 'Extended Warranty',
      vendors: [
        { vendorId: '1', amount: 0 },
        { vendorId: '2', amount: 12000 },
        { vendorId: '3', amount: 15000 }
      ]
    },
    {
      category: 'Spare Parts (Est.)',
      vendors: [
        { vendorId: '1', amount: 18000 },
        { vendorId: '2', amount: 22000 },
        { vendorId: '3', amount: 20000 }
      ]
    }
  ]
};

// Vendor Performance Data for Charts
export const vendorPerformanceData = [
  { name: 'Precision Machinery', onTime: 96, quality: 98, orders: 24 },
  { name: 'TechParts Intl', onTime: 92, quality: 95, orders: 18 },
  { name: 'AutomaTech', onTime: 99, quality: 99, orders: 12 },
  { name: 'QualityFirst', onTime: 94, quality: 97, orders: 15 },
  { name: 'GlobalTools', onTime: 88, quality: 90, orders: 32 },
  { name: 'Swiss Precision', onTime: 100, quality: 100, orders: 8 }
];

// Budget Trend Data for Dashboard
export const budgetTrendData = [
  { month: 'Aug', budget: 1200000, spent: 980000 },
  { month: 'Sep', budget: 1350000, spent: 1150000 },
  { month: 'Oct', budget: 1500000, spent: 1380000 },
  { month: 'Nov', budget: 1650000, spent: 1520000 },
  { month: 'Dec', budget: 1750000, spent: 1680000 },
  { month: 'Jan', budget: 1800000, spent: 1420000 }
];

// RFQ Status Distribution
export const rfqStatusData = [
  { name: 'Open', value: 3, color: '#3b82f6' },
  { name: 'Closed', value: 1, color: '#22c55e' },
  { name: 'Draft', value: 1, color: '#9ca3af' },
  { name: 'Awarded', value: 1, color: '#8b5cf6' }
];

// Category Distribution
export const categoryData = [
  { name: 'Manufacturing', value: 5, color: '#3b82f6' },
  { name: 'Quality', value: 2, color: '#22c55e' },
  { name: 'Automation', value: 1, color: '#f97316' }
];

// Recent Activity
export const recentActivity = [
  { id: 1, type: 'rfq', message: 'RFQ-2024-003 received 2 new responses', time: '2 hours ago' },
  { id: 2, type: 'approval', message: 'PO-2024-012 approved by Finance', time: '4 hours ago' },
  { id: 3, type: 'vendor', message: 'New vendor registration: NewVendor Systems', time: '6 hours ago' },
  { id: 4, type: 'equipment', message: 'CMM System marked as delivered', time: '1 day ago' },
  { id: 5, type: 'evaluation', message: 'TBE completed for RFQ-2024-001', time: '2 days ago' }
];
