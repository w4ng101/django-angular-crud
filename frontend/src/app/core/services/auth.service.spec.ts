import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AuthService } from './auth.service';
import { User } from '../models/auth.model';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  const API_URL = 'http://localhost:8000/api';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    
    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    it('should login user and store tokens', () => {
      const mockResponse = {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          profile: {
            role: 3,
            role_display: 'User',
            phone: '',
            address: '',
            created_at: '2026-02-19T10:00:00Z',
            updated_at: '2026-02-19T10:00:00Z'
          }
        }
      };

      const credentials = { username: 'testuser', password: 'password123' };

      service.login(credentials).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(localStorage.getItem('access_token')).toBe('mock-access-token');
        expect(localStorage.getItem('refresh_token')).toBe('mock-refresh-token');
        expect(localStorage.getItem('currentUser')).toBe(JSON.stringify(mockResponse.user));
      });

      const req = httpMock.expectOne(`${API_URL}/auth/login/`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(credentials);
      req.flush(mockResponse);
    });
  });

  describe('logout', () => {
    it('should clear tokens and user data', () => {
      localStorage.setItem('access_token', 'test-token');
      localStorage.setItem('refresh_token', 'test-refresh');
      localStorage.setItem('currentUser', JSON.stringify({ id: 1 }));

      service.logout();

      expect(localStorage.getItem('access_token')).toBeNull();
      expect(localStorage.getItem('refresh_token')).toBeNull();
      expect(localStorage.getItem('currentUser')).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when access token exists', () => {
      localStorage.setItem('access_token', 'test-token');
      expect(service.isAuthenticated()).toBe(true);
    });

    it('should return false when access token does not exist', () => {
      localStorage.removeItem('access_token');
      expect(service.isAuthenticated()).toBe(false);
    });
  });

  describe('getCurrentUser', () => {
    it('should return current user from localStorage', () => {
      const mockUser: User = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        profile: {
          role: 3,
          role_display: 'User',
          phone: '',
          address: '',
          created_at: '2026-02-19T10:00:00Z',
          updated_at: '2026-02-19T10:00:00Z'
        }
      };
      localStorage.setItem('currentUser', JSON.stringify(mockUser));

      const user = service.getCurrentUser();
      expect(user).toEqual(mockUser);
    });

    it('should return null when no user in localStorage', () => {
      localStorage.removeItem('currentUser');
      expect(service.getCurrentUser()).toBeNull();
    });
  });

  describe('getUserRole', () => {
    it('should return user role', () => {
      const mockUser: User = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        profile: {
          role: 2,
          role_display: 'Admin',
          phone: '',
          address: '',
          created_at: '2026-02-19T10:00:00Z',
          updated_at: '2026-02-19T10:00:00Z'
        }
      };
      localStorage.setItem('currentUser', JSON.stringify(mockUser));

      expect(service.getUserRole()).toBe(2);
    });

    it('should return 3 (User) when no user exists', () => {
      localStorage.removeItem('currentUser');
      expect(service.getUserRole()).toBe(3);
    });
  });

  describe('isSuperAdmin', () => {
    it('should return true for super admin', () => {
      const mockUser: User = {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        profile: {
          role: 1,
          role_display: 'Super Admin',
          phone: '',
          address: '',
          created_at: '2026-02-19T10:00:00Z',
          updated_at: '2026-02-19T10:00:00Z'
        }
      };
      localStorage.setItem('currentUser', JSON.stringify(mockUser));

      expect(service.isSuperAdmin()).toBe(true);
    });

    it('should return false for non-super admin', () => {
      const mockUser: User = {
        id: 1,
        username: 'user',
        email: 'user@example.com',
        profile: {
          role: 3,
          role_display: 'User',
          phone: '',
          address: '',
          created_at: '2026-02-19T10:00:00Z',
          updated_at: '2026-02-19T10:00:00Z'
        }
      };
      localStorage.setItem('currentUser', JSON.stringify(mockUser));

      expect(service.isSuperAdmin()).toBe(false);
    });
  });

  describe('isAdmin', () => {
    it('should return true for admin or super admin', () => {
      const mockAdmin: User = {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        profile: {
          role: 2,
          role_display: 'Admin',
          phone: '',
          address: ''
        }
      };
      localStorage.setItem('currentUser', JSON.stringify(mockAdmin));
      expect(service.isAdmin()).toBe(true);

      const mockSuperAdmin: User = {
        ...mockAdmin,
        profile: { ...mockAdmin.profile, role: 1, role_display: 'Super Admin' }
      };
      localStorage.setItem('currentUser', JSON.stringify(mockSuperAdmin));
      expect(service.isAdmin()).toBe(true);
    });

    it('should return false for regular user', () => {
      const mockUser: User = {
        id: 1,
        username: 'user',
        email: 'user@example.com',
        profile: {
          role: 3,
          role_display: 'User',
          phone: '',
          address: '',
          created_at: '2026-02-19T10:00:00Z',
          updated_at: '2026-02-19T10:00:00Z'
        }
      };
      localStorage.setItem('currentUser', JSON.stringify(mockUser));

      expect(service.isAdmin()).toBe(false);
    });
  });
});
