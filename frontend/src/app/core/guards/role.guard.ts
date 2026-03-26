import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { UserRole } from '../models/auth.model';

export const roleGuard = (requiredRole: UserRole): CanActivateFn => {
  return () => {
    const authService = inject(AuthService);
    const router = inject(Router);

    if (!authService.isAuthenticated()) {
      router.navigate(['/login']);
      return false;
    }

    const userRole = authService.getUserRole();
    
    // Check if user has the required role level (lower number = higher privileges)
    if (userRole !== null && userRole <= requiredRole) {
      return true;
    }

    // Redirect to dashboard if user doesn't have the required role
    router.navigate(['/dashboard']);
    return false;
  };
};

export const superAdminGuard: CanActivateFn = roleGuard(UserRole.SUPER_ADMIN);
export const adminGuard: CanActivateFn = roleGuard(UserRole.ADMIN);
export const userGuard: CanActivateFn = roleGuard(UserRole.USER);
