/**
 * TypeScript type definitions for HackSeek frontend.
 */

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface Hackathon {
  id: string;
  title: string;
  description?: string;
  short_description?: string;
  organizer?: string;
  website_url?: string;
  registration_url?: string;
  image_url?: string;
  start_date?: string;
  end_date?: string;
  registration_deadline?: string;
  location?: string;
  is_online: boolean;
  is_hybrid: boolean;
  participation_fee?: number;
  prize_money?: number;
  max_participants?: number;
  difficulty_level?: 'Beginner' | 'Intermediate' | 'Advanced' | 'All';
  categories?: string[];
  technologies?: string[];
  source_platform?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SearchFilters {
  q?: string;
  location?: string;
  categories?: string[];
  technologies?: string[];
  is_online?: boolean;
  min_prize?: number;
  difficulty_level?: string;
  date_range?: string;
  sort?: string;
  page?: number;
  size?: number;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  timestamp: string;
}

export interface FilterOption {
  label: string;
  value: string;
  count?: number;
}

export interface SortOption {
  label: string;
  value: string;
  direction: 'asc' | 'desc';
}

export interface CalendarEvent {
  title: string;
  start: Date;
  end: Date;
  url?: string;
  description?: string;
}