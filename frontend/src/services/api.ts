import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  RFQ,
  Vendor,
  EquipmentData,
  DashboardStats,
  VendorComparison,
  Quotation,
  TBEEvaluation,
  PurchaseOrder,
  GanttTask,
  PaginatedResponse,
  ApiResponse,
  EquipmentType,
  ActivityItem,
} from '../types';

// API base URL - defaults to Railway deployment URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor for logging and auth
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================
// RFQ API
// ============================================

export const rfqApi = {
  list: async (params?: {
    page?: number;
    limit?: number;
    status?: string;
    project_id?: string;
  }): Promise<PaginatedResponse<RFQ>> => {
    const response = await apiClient.get('/rfqs', { params });
    return response.data;
  },

  get: async (id: string): Promise<ApiResponse<RFQ>> => {
    const response = await apiClient.get(`/rfqs/${id}`);
    return response.data;
  },

  parse: async (equipment: EquipmentType): Promise<ApiResponse<EquipmentData[]>> => {
    const response = await apiClient.get(`/rfq/parse/${equipment}`);
    return response.data;
  },

  create: async (data: Partial<RFQ>): Promise<ApiResponse<RFQ>> => {
    const response = await apiClient.post('/rfqs', data);
    return response.data;
  },

  update: async (id: string, data: Partial<RFQ>): Promise<ApiResponse<RFQ>> => {
    const response = await apiClient.put(`/rfqs/${id}`, data);
    return response.data;
  },
};

// ============================================
// Vendor API
// ============================================

export const vendorApi = {
  list: async (params?: {
    page?: number;
    limit?: number;
    is_approved?: boolean;
    search?: string;
  }): Promise<PaginatedResponse<Vendor>> => {
    const response = await apiClient.get('/vendors', { params });
    return response.data;
  },

  get: async (id: string): Promise<ApiResponse<Vendor>> => {
    const response = await apiClient.get(`/vendors/${id}`);
    return response.data;
  },

  create: async (data: Partial<Vendor>): Promise<ApiResponse<Vendor>> => {
    const response = await apiClient.post('/vendors', data);
    return response.data;
  },

  approve: async (id: string): Promise<ApiResponse<Vendor>> => {
    const response = await apiClient.post(`/vendors/${id}/approve`);
    return response.data;
  },

  compare: async (vendorIds: string[], equipmentType?: EquipmentType): Promise<ApiResponse<VendorComparison[]>> => {
    const response = await apiClient.get('/vendors/compare', {
      params: { vendor_ids: vendorIds.join(','), equipment_type: equipmentType },
    });
    return response.data;
  },
};

// ============================================
// Equipment Data API
// ============================================

export const equipmentApi = {
  list: async (params?: {
    equipment_type?: EquipmentType;
    vendor_id?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<EquipmentData>> => {
    const response = await apiClient.get('/equipment', { params });
    return response.data;
  },

  parseFromSharePoint: async (equipment: EquipmentType): Promise<ApiResponse<EquipmentData[]>> => {
    const response = await apiClient.get(`/rfq/parse/${equipment}`);
    return response.data;
  },

  getTBEScores: async (equipmentType?: EquipmentType): Promise<ApiResponse<EquipmentData[]>> => {
    const response = await apiClient.get('/tbe-scores', { params: { equipment_type: equipmentType } });
    return response.data;
  },
};

// ============================================
// TBE Evaluation API
// ============================================

export const tbeApi = {
  list: async (params?: {
    rfq_id?: string;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<TBEEvaluation[]>> => {
    const response = await apiClient.get('/tbe-evaluations', { params });
    return response.data;
  },

  get: async (id: string): Promise<ApiResponse<TBEEvaluation>> => {
    const response = await apiClient.get(`/tbe-evaluations/${id}`);
    return response.data;
  },

  calculate: async (id: string): Promise<ApiResponse<unknown>> => {
    const response = await apiClient.post(`/tbe-evaluations/${id}/calculate`);
    return response.data;
  },

  getScores: async (): Promise<ApiResponse<EquipmentData[]>> => {
    const response = await apiClient.get('/tbe-scores');
    return response.data;
  },
};

// ============================================
// Quotation API
// ============================================

export const quotationApi = {
  list: async (params?: {
    rfq_id?: string;
    vendor_id?: string;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<Quotation[]>> => {
    const response = await apiClient.get('/quotations', { params });
    return response.data;
  },

  compare: async (rfqId: string): Promise<ApiResponse<VendorComparison[]>> => {
    const response = await apiClient.get(`/rfqs/${rfqId}/quotations/compare`);
    return response.data;
  },
};

// ============================================
// Purchase Order API
// ============================================

export const purchaseOrderApi = {
  list: async (params?: {
    status?: string;
    vendor_id?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<PurchaseOrder>> => {
    const response = await apiClient.get('/purchase-orders', { params });
    return response.data;
  },

  get: async (id: string): Promise<ApiResponse<PurchaseOrder>> => {
    const response = await apiClient.get(`/purchase-orders/${id}`);
    return response.data;
  },
};

// ============================================
// Dashboard & Reports API
// ============================================

export const dashboardApi = {
  getStats: async (): Promise<ApiResponse<DashboardStats>> => {
    const response = await apiClient.get('/reports/dashboard');
    return response.data;
  },

  getProcurementSummary: async (params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<ApiResponse<unknown>> => {
    const response = await apiClient.get('/reports/procurement-summary', { params });
    return response.data;
  },

  getVendorPerformance: async (): Promise<ApiResponse<unknown>> => {
    const response = await apiClient.get('/reports/vendor-performance');
    return response.data;
  },

  getRecentActivity: async (): Promise<ApiResponse<ActivityItem[]>> => {
    const response = await apiClient.get('/reports/activity');
    return response.data;
  },
};

// ============================================
// Timeline API
// ============================================

export const timelineApi = {
  getTasks: async (params?: {
    vendor_id?: string;
    equipment_type?: EquipmentType;
  }): Promise<ApiResponse<GanttTask[]>> => {
    const response = await apiClient.get('/timeline/tasks', { params });
    return response.data;
  },

  updateTask: async (id: string, data: Partial<GanttTask>): Promise<ApiResponse<GanttTask>> => {
    const response = await apiClient.put(`/timeline/tasks/${id}`, data);
    return response.data;
  },
};

export default apiClient;
