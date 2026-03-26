import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { roleGuard, superAdminGuard, adminGuard, userGuard } from './role.guard';
import { AuthService } from '../services/auth.service';
import { UserRole } from '../models/auth.model';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';

describe('roleGuard', () => {
  let authService: jest.Mocked<AuthService>;
  let router: Router;

  const mockRoute = {} as ActivatedRouteSnapshot;
  const mockState = {} as RouterStateSnapshot;

  beforeEach(() => {
    const authServiceMock = {
      isAuthenticated: jest.fn(),
      getUserRole: jest.fn(),
    };

    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(),
        { provide: AuthService, useValue: authServiceMock },
      ],
    });

    authService = TestBed.inject(AuthService) as jest.Mocked<AuthService>;
    router = TestBed.inject(Router);
  });

  describe('when not authenticated', () => {
    it('should redirect to login and return false', () => {
      authService.isAuthenticated.mockReturnValue(false);
      const navigateSpy = jest.spyOn(router, 'navigate');

      const guard = roleGuard(UserRole.USER);
      const result = TestBed.runInInjectionContext(() =>
        guard(mockRoute, mockState)
      );

      expect(result).toBe(false);
      expect(navigateSpy).toHaveBeenCalledWith(['/login']);
    });
  });

  describe('when authenticated', () => {
    beforeEach(() => {
      authService.isAuthenticated.mockReturnValue(true);
    });

    it('should allow super admin to access super admin routes', () => {
      authService.getUserRole.mockReturnValue(UserRole.SUPER_ADMIN);

      const guard = roleGuard(UserRole.SUPER_ADMIN);
      const result = TestBed.runInInjectionContext(() =>
        guard(mockRoute, mockState)
      );

      expect(result).toBe(true);
    });

    it('should allow super admin to access admin routes', () => {
      authService.getUserRole.mockReturnValue(UserRole.SUPER_ADMIN);

      const guard = roleGuard(UserRole.ADMIN);
      const result = TestBed.runInInjectionContext(() =>
        guard(mockRoute, mockState)
      );

      expect(result).toBe(true);
    });

    it('should allow admin to access admin routes', () => {
      authService.getUserRole.mockReturnValue(UserRole.ADMIN);

      const guard = roleGuard(UserRole.ADMIN);
      const result = TestBed.runInInjectionContext(() =>
        guard(mockRoute, mockState)
      );

      expect(result).toBe(true);
    });

    it('should deny admin from super admin only routes', () => {
      authService.getUserRole.mockReturnValue(UserRole.ADMIN);
      const navigateSpy = jest.spyOn(router, 'navigate');

      const guard = roleGuard(UserRole.SUPER_ADMIN);
      const result = TestBed.runInInjectionContext(() =>
        guard(mockRoute, mockState)
      );

      expect(result).toBe(false);
      expect(navigateSpy).toHaveBeenCalledWith(['/dashboard']);
    });

    it('should deny regular user from admin routes', () => {
      authService.getUserRole.mockReturnValue(UserRole.USER);
      const navigateSpy = jest.spyOn(router, 'navigate');

      const guard = roleGuard(UserRole.ADMIN);
      const result = TestBed.runInInjectionContext(() =>
        guard(mockRoute, mockState)
      );

      expect(result).toBe(false);
      expect(navigateSpy).toHaveBeenCalledWith(['/dashboard']);
    });

    it('should allow all authenticated users to access user routes', () => {
      authService.getUserRole.mockReturnValue(UserRole.USER);

      const guard = roleGuard(UserRole.USER);
      const result = TestBed.runInInjectionContext(() =>
        guard(mockRoute, mockState)
      );

      expect(result).toBe(true);
    });

    it('should deny when role is null', () => {
      authService.getUserRole.mockReturnValue(null);
      const navigateSpy = jest.spyOn(router, 'navigate');

      const guard = roleGuard(UserRole.USER);
      const result = TestBed.runInInjectionContext(() =>
        guard(mockRoute, mockState)
      );

      expect(result).toBe(false);
      expect(navigateSpy).toHaveBeenCalledWith(['/dashboard']);
    });
  });
});

describe('superAdminGuard', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(),
        {
          provide: AuthService,
          useValue: { isAuthenticated: jest.fn().mockReturnValue(true), getUserRole: jest.fn().mockReturnValue(UserRole.SUPER_ADMIN) },
        },
      ],
    });
  });

  it('should allow super admin', () => {
    const result = TestBed.runInInjectionContext(() =>
      superAdminGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot)
    );
    expect(result).toBe(true);
  });
});

describe('adminGuard', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(),
        {
          provide: AuthService,
          useValue: { isAuthenticated: jest.fn().mockReturnValue(true), getUserRole: jest.fn().mockReturnValue(UserRole.ADMIN) },
        },
      ],
    });
  });

  it('should allow admin', () => {
    const result = TestBed.runInInjectionContext(() =>
      adminGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot)
    );
    expect(result).toBe(true);
  });
});

describe('userGuard', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        provideHttpClient(),
        {
          provide: AuthService,
          useValue: { isAuthenticated: jest.fn().mockReturnValue(true), getUserRole: jest.fn().mockReturnValue(UserRole.USER) },
        },
      ],
    });
  });

  it('should allow regular user', () => {
    const result = TestBed.runInInjectionContext(() =>
      userGuard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot)
    );
    expect(result).toBe(true);
  });
});
