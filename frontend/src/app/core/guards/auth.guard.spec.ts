import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { authGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';

describe('authGuard', () => {
  let authService: jest.Mocked<AuthService>;
  let router: Router;

  const mockRoute = {} as ActivatedRouteSnapshot;
  const mockState = { url: '/dashboard' } as RouterStateSnapshot;

  beforeEach(() => {
    const authServiceMock = {
      isAuthenticated: jest.fn(),
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

  it('should allow access when user is authenticated', () => {
    authService.isAuthenticated.mockReturnValue(true);

    const result = TestBed.runInInjectionContext(() =>
      authGuard(mockRoute, mockState)
    );

    expect(result).toBe(true);
  });

  it('should deny access and navigate to login when not authenticated', () => {
    authService.isAuthenticated.mockReturnValue(false);
    const navigateSpy = jest.spyOn(router, 'navigate');

    const result = TestBed.runInInjectionContext(() =>
      authGuard(mockRoute, mockState)
    );

    expect(result).toBe(false);
    expect(navigateSpy).toHaveBeenCalledWith(
      ['/login'],
      { queryParams: { returnUrl: '/dashboard' } }
    );
  });

  it('should pass returnUrl as query param when redirecting', () => {
    authService.isAuthenticated.mockReturnValue(false);
    const navigateSpy = jest.spyOn(router, 'navigate');
    const stateWithUrl = { url: '/tasks/123' } as RouterStateSnapshot;

    TestBed.runInInjectionContext(() =>
      authGuard(mockRoute, stateWithUrl)
    );

    expect(navigateSpy).toHaveBeenCalledWith(
      ['/login'],
      { queryParams: { returnUrl: '/tasks/123' } }
    );
  });
});
