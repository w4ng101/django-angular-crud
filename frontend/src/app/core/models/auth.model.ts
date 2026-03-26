export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  profile?: UserProfile;
}

export interface UserProfile {
  role: number;
  role_display: string;
  phone?: string;
  address?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
  role?: number;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
  message?: string;
}

export interface TokenRefreshResponse {
  access: string;
}

// Role constants
export enum UserRole {
  SUPER_ADMIN = 1,
  ADMIN = 2,
  USER = 3
}

export const UserRoleDisplay = {
  [UserRole.SUPER_ADMIN]: 'Super Admin',
  [UserRole.ADMIN]: 'Admin',
  [UserRole.USER]: 'User'
};

