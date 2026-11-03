// ==========================================
// Generic API Envelope
// ==========================================
export interface ApiResponse<T> {
  status: 'success' | 'error';
  message?: string;
  data: T;
}

export interface ApiErrorResponse {
  detail: string | Array<{ loc: string[]; msg: string; type: string }>;
}

// ==========================================
// Authentication Types
// ==========================================
export type UserRole = 'admin' | 'user';

export interface UserProfile {
  id: string; // UUID
  email: string;
  full_name: string;
  role: UserRole;
  phone_number?: string | null;
  is_active?: boolean;
  created_at?: string | null;
}

export interface LoginResponseData {
  access_token: string;
  token_type: 'bearer' | string;
  user: UserProfile;
}

// ==========================================
// Master Category Types
// ==========================================
export interface WasteCategory {
  id: number;
  slug: string;
  name: string;
  description?: string | null;
  badge_color: string;
}

export interface CategoryBrief {
  id: number;
  name: string;
  badge_color: string;
  slug?: string | null;
}

export interface ReporterBrief {
  id: string;
  full_name: string;
  email?: string | null;
}

// ==========================================
// Waste Report Types
// ==========================================
export type ReportStatus = 'Pending' | 'In Progress' | 'Completed' | 'Rejected';

export interface ReportListItem {
  id: string; // UUID
  title: string;
  image_url: string;
  latitude: number;
  longitude: number;
  status: ReportStatus;
  created_at: string;
  category: CategoryBrief;
  reporter: ReporterBrief;
}

export interface ReportLogItem {
  id: string; // UUID
  previous_status?: string | null;
  new_status: string;
  actor_id?: string | null;
  remarks?: string | null;
  created_at: string;
}

export interface ReportDetailData {
  id: string; // UUID
  title: string;
  description?: string | null;
  image_url: string;
  detected_category?: string | null;
  ai_confidence?: number;
  latitude: number;
  longitude: number;
  address_note?: string | null;
  status: ReportStatus;
  admin_notes?: string | null;
  resolved_at?: string | null;
  created_at: string;
  updated_at: string;
  category: CategoryBrief;
  reporter: ReporterBrief;
  logs: ReportLogItem[];
}

export interface PaginationMeta {
  total_items: number;
  current_page: number;
  total_pages: number;
  limit: number;
}

export interface ReportListResponse {
  status: 'success';
  meta: PaginationMeta;
  data: ReportListItem[];
}

export interface StatusUpdatePayload {
  status: ReportStatus;
  admin_notes?: string;
}

// ==========================================
// Dashboard Stats Types
// ==========================================
export interface DashboardSummary {
  total_reports: number;
  pending_count: number;
  in_progress_count: number;
  completed_count: number;
  rejected_count: number;
  completion_rate_percent: number;
  active_users?: number | null;
}

export interface CategoryDistributionItem {
  category: string;
  count: number;
  percentage: number;
}

export interface RecentActivityItem {
  report_id: string;
  action: string;
  timestamp: string;
}

export interface DashboardStatsData {
  summary: DashboardSummary;
  category_distribution: CategoryDistributionItem[];
  recent_activities: RecentActivityItem[];
}

export interface DashboardStatsResponse {
  status: 'success';
  data: DashboardStatsData;
}

// ==========================================
// ML Prediction Types
// ==========================================
export interface PredictResponseData {
  category: string;
  confidence: number;
  confidence_percentage?: string;
  category_id?: number;
  probabilities?: Record<string, number>;
}

// ==========================================
// User Management Types
// ==========================================
export interface UserListItem {
  id: string; // UUID
  email: string;
  full_name: string;
  role: UserRole;
  phone_number?: string | null;
  is_active: boolean;
  total_reports: number;
  created_at?: string | null;
}

export interface UserListResponse {
  status: 'success';
  data: UserListItem[];
}
