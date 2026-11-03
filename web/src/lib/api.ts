import axios, { AxiosError } from 'axios';
import type {
  ApiResponse,
  LoginResponseData,
  UserProfile,
  WasteCategory,
  ReportDetailData,
  ReportListResponse,
  StatusUpdatePayload,
  DashboardStatsResponse,
  UserListResponse,
} from '@/types/api';

const DEFAULT_API_BASE = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_BASE,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Bearer token from localStorage
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 Unauthorized by clearing storage and redirecting to /login
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Resolves static media relative paths (e.g. /uploads/reports/...)
 * to full browser image URLs using the backend origin.
 */
export function getFullImageUrl(path?: string | null, baseUrl?: string): string {
  if (!path) {
    return '/placeholder.png';
  }
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  const base = baseUrl || process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_BASE;
  const origin = base.replace(/\/api\/v1\/?$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${origin}${cleanPath}`;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  password: string;
  phone_number?: string;
}

export interface ReportsQueryParams {
  status?: string;
  category_id?: number;
  search?: string;
  page?: number;
  limit?: number;
}

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<ApiResponse<LoginResponseData>> => {
    const res = await apiClient.post<ApiResponse<LoginResponseData>>('/auth/login', credentials);
    return res.data;
  },
  getMe: async (): Promise<ApiResponse<UserProfile>> => {
    const res = await apiClient.get<ApiResponse<UserProfile>>('/auth/me');
    return res.data;
  },
  register: async (data: RegisterPayload): Promise<ApiResponse<UserProfile>> => {
    const res = await apiClient.post<ApiResponse<UserProfile>>('/auth/register', data);
    return res.data;
  },
};

export const dashboardApi = {
  getStats: async (): Promise<DashboardStatsResponse> => {
    const res = await apiClient.get<DashboardStatsResponse>('/dashboard/stats');
    return res.data;
  },
};

export const reportsApi = {
  getReports: async (params?: ReportsQueryParams): Promise<ReportListResponse> => {
    const res = await apiClient.get<ReportListResponse>('/reports', { params });
    return res.data;
  },
  getReport: async (id: string): Promise<ApiResponse<ReportDetailData>> => {
    const res = await apiClient.get<ApiResponse<ReportDetailData>>(`/reports/${id}`);
    return res.data;
  },
  updateStatus: async (
    id: string,
    payload: StatusUpdatePayload
  ): Promise<ApiResponse<ReportDetailData>> => {
    const res = await apiClient.patch<ApiResponse<ReportDetailData>>(
      `/reports/${id}/status`,
      payload
    );
    return res.data;
  },
};

export const categoriesApi = {
  getCategories: async (): Promise<ApiResponse<WasteCategory[]>> => {
    const res = await apiClient.get<ApiResponse<WasteCategory[]>>('/categories');
    return res.data;
  },
};

export interface UsersQueryParams {
  search?: string;
  role?: string;
}

export const usersApi = {
  getUsers: async (params?: UsersQueryParams): Promise<UserListResponse> => {
    const res = await apiClient.get<UserListResponse>('/users', { params });
    return res.data;
  },
};

export default apiClient;
