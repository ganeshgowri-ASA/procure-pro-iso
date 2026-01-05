// Equipment Types
export interface Equipment {
  id: string;
  equipmentId: string;
  name: string;
  category: string;
  manufacturer: string;
  model: string;
  specifications: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  status: 'Active' | 'Pending' | 'Ordered' | 'Delivered';
  rfqStatus: 'Assigned' | 'Pending' | 'Completed';
  attachments?: string[];
  createdAt: string;
  updatedAt: string;
}

// RFQ Types
export interface RFQ {
  id: string;
  rfqNumber: string;
  title: string;
  description: string;
  status: 'Draft' | 'Open' | 'Closed' | 'Awarded' | 'Cancelled';
  priority: 'Low' | 'Normal' | 'High' | 'Critical';
  issueDate: string;
  closingDate: string;
  estimatedValue: number;
  vendorsInvited: number;
  responsesReceived: number;
  attachments?: string[];
  items: RFQItem[];
  createdAt: string;
}

export interface RFQItem {
  id: string;
  description: string;
  quantity: number;
  unit: string;
  targetPrice?: number;
}

// Vendor Types
export interface Vendor {
  id: string;
  vendorCode: string;
  companyName: string;
  contactPerson: string;
  email: string;
  phone: string;
  country: string;
  category: string;
  rating: number;
  status: 'Approved' | 'Pending' | 'Blacklisted';
  certifications: string[];
  totalOrders: number;
  totalValue: number;
  onTimeDelivery: number;
  qualityScore: number;
}

// Technical Evaluation Types
export interface TechnicalEvaluation {
  id: string;
  rfqId: string;
  rfqTitle: string;
  status: 'Draft' | 'In Progress' | 'Completed' | 'Approved';
  vendors: VendorScore[];
  ctqMatrix: CTQItem[];
  createdAt: string;
}

export interface VendorScore {
  vendorId: string;
  vendorName: string;
  overallScore: number;
  technicalScore: number;
  qualityScore: number;
  deliveryScore: number;
  complianceScore: number;
  recommendation: 'Recommended' | 'Acceptable' | 'Not Recommended';
}

export interface CTQItem {
  id: string;
  parameter: string;
  weight: number;
  requirement: string;
  vendors: {
    vendorId: string;
    value: string;
    score: number;
    compliant: boolean;
  }[];
}

// Commercial Evaluation Types
export interface CommercialEvaluation {
  id: string;
  rfqId: string;
  rfqTitle: string;
  status: 'Draft' | 'In Progress' | 'Completed' | 'Approved';
  vendors: VendorPricing[];
  tcoComparison: TCOItem[];
}

export interface VendorPricing {
  vendorId: string;
  vendorName: string;
  unitPrice: number;
  quantity: number;
  subtotal: number;
  discount: number;
  tax: number;
  shipping: number;
  total: number;
  paymentTerms: string;
  deliveryDays: number;
  warranty: string;
}

export interface TCOItem {
  category: string;
  vendors: {
    vendorId: string;
    amount: number;
  }[];
}

// Dashboard KPI Types
export interface KPI {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  color: 'blue' | 'green' | 'orange' | 'purple';
  icon: string;
}
