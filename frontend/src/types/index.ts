// Equipment types for procurement
export type EquipmentType =
  | 'DSC'
  | 'TGA'
  | 'Chamber'
  | 'Spectrometer'
  | 'Chromatograph'
  | 'Microscope'
  | 'Analyzer'
  | 'Other';

// RFQ (Request for Quotation) types
export interface RFQ {
  id: string;
  rfq_number: string;
  title: string;
  description?: string;
  status: RFQStatus;
  issue_date?: string;
  closing_date?: string;
  currency: string;
  estimated_value?: number;
  project_number?: string;
  project_name?: string;
  item_count: number;
  quotation_count: number;
  created_at: string;
  equipment_type?: EquipmentType;
}

export type RFQStatus = 'draft' | 'open' | 'closed' | 'awarded' | 'cancelled';

// Vendor types
export interface Vendor {
  id: string;
  vendor_code: string;
  company_name: string;
  contact_person?: string;
  email: string;
  phone?: string;
  city?: string;
  country?: string;
  is_approved: boolean;
  rating?: number;
  created_at: string;
}

// Equipment analysis data from parsed Excel
export interface EquipmentData {
  id: string;
  equipment: string;
  equipment_type: EquipmentType;
  vendor: string;
  vendor_id?: string;
  technical_specs: TechnicalSpecs;
  price: number;
  currency: string;
  timeline: TimelineInfo;
  tbe_score: TBEScore;
  compliance_status: 'compliant' | 'partial' | 'non-compliant';
}

export interface TechnicalSpecs {
  model: string;
  manufacturer: string;
  specifications: string[];
  features: string[];
  warranty_months: number;
}

export interface TimelineInfo {
  lead_time_days: number;
  delivery_date?: string;
  installation_days?: number;
  training_days?: number;
}

export interface TBEScore {
  overall: number;
  technical: number;
  commercial: number;
  delivery: number;
  compliance: number;
  rank?: number;
}

// Vendor comparison data
export interface VendorComparison {
  vendor_id: string;
  vendor_name: string;
  equipment_type: EquipmentType;
  total_price: number;
  average_tbe_score: number;
  technical_score: number;
  delivery_score: number;
  compliance_score: number;
  items_quoted: number;
  items: EquipmentData[];
}

// Dashboard statistics
export interface DashboardStats {
  active_projects: number;
  open_rfqs: number;
  active_pos: number;
  approved_vendors: number;
  total_po_value: number;
  recent_quotations: number;
}

// Activity feed item
export interface ActivityItem {
  id: string;
  type: 'rfq_created' | 'quotation_received' | 'po_issued' | 'vendor_approved' | 'tbe_completed';
  title: string;
  description: string;
  timestamp: string;
  entity_id: string;
  entity_type: string;
  user?: string;
}

// Quotation types
export interface Quotation {
  id: string;
  quotation_number: string;
  rfq_id: string;
  rfq_number?: string;
  vendor_id: string;
  vendor_name: string;
  status: 'submitted' | 'under_review' | 'accepted' | 'rejected';
  submission_date: string;
  total_amount?: number;
  currency: string;
  overall_score?: number;
  rank?: number;
}

// TBE Evaluation types
export interface TBEEvaluation {
  id: string;
  evaluation_number: string;
  title: string;
  status: 'draft' | 'in_progress' | 'completed' | 'approved';
  evaluation_date?: string;
  rfq_number: string;
  selected_vendor?: string;
  created_at: string;
}

// Purchase Order types
export interface PurchaseOrder {
  id: string;
  po_number: string;
  status: 'draft' | 'approved' | 'sent' | 'acknowledged' | 'completed' | 'cancelled';
  po_date?: string;
  delivery_date?: string;
  total_amount?: number;
  currency: string;
  vendor_name: string;
  project_number?: string;
  created_at: string;
}

// API Response types
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Timeline/Gantt chart types
export interface GanttTask {
  id: string;
  name: string;
  equipment_type: EquipmentType;
  vendor: string;
  start_date: string;
  end_date: string;
  progress: number;
  status: 'pending' | 'in_progress' | 'completed' | 'delayed';
  dependencies?: string[];
}

// Filter types
export interface FilterState {
  equipment_type?: EquipmentType;
  vendor_id?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
}

// Sort types
export interface SortState {
  field: string;
  direction: 'asc' | 'desc';
}
