import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { User, UserRoleDisplay } from '../../../core/models/auth.model';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <nav class="modern-navbar">
      <div class="navbar-wrapper">
        <div class="navbar-brand">
          <div class="logo-gradient">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="url(#logo-gradient)"/>
              <path d="M8 12h16M8 16h16M8 20h10" stroke="white" stroke-width="2" stroke-linecap="round"/>
              <defs>
                <linearGradient id="logo-gradient" x1="0" y1="0" x2="32" y2="32">
                  <stop offset="0%" stop-color="#f093fb"/>
                  <stop offset="100%" stop-color="#f5576c"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1>TaskFlow</h1>
          <span *ngIf="currentUser" class="user-badge" [class]="getRoleBadgeClass()">
            {{ getRoleDisplay() }}
          </span>
        </div>
        
        <button class="mobile-menu-toggle" (click)="toggleMobileMenu()" type="button" aria-label="Toggle menu">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" *ngIf="!mobileMenuOpen">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" *ngIf="mobileMenuOpen">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
        
        <div class="navbar-menu" [class.active]="mobileMenuOpen">
          <div class="menu-content">
            <div class="menu-items">
              <a routerLink="/dashboard" routerLinkActive="active" (click)="closeMobileMenu()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
                </svg>
                Dashboard
              </a>
              <a routerLink="/tasks" routerLinkActive="active" (click)="closeMobileMenu()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                </svg>
                Tasks
              </a>
              <a *ngIf="isAdmin()" routerLink="/admin" class="admin-link" (click)="closeMobileMenu()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                Admin
              </a>
              <a routerLink="/profile" routerLinkActive="active" (click)="closeMobileMenu()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                Profile
              </a>
            </div>
            <div class="menu-footer">
              <div class="user-info" *ngIf="currentUser">
                <div class="user-avatar">
                  {{ currentUser.username.charAt(0).toUpperCase() }}
                </div>
                <div class="user-details">
                  <div class="user-name">{{ currentUser.username }}</div>
                  <div class="user-email">{{ currentUser.email }}</div>
                </div>
              </div>
              <button class="logout-btn" (click)="logout()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  `,
  styles: [`
    .modern-navbar {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      position: sticky;
      top: 0;
      z-index: 1000;
      backdrop-filter: blur(10px);
    }

    .navbar-wrapper {
      max-width: 1280px;
      margin: 0 auto;
      padding: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
    }

    .navbar-brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      z-index: 1001;
    }

    .logo-gradient {
      display: flex;
      align-items: center;
      animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-5px); }
    }

    .navbar-brand h1 {
      font-size: 1.5rem;
      font-weight: 700;
      color: white;
      margin: 0;
      letter-spacing: -0.02em;
    }

    .user-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      background: rgba(255, 255, 255, 0.2);
      color: white;
      backdrop-filter: blur(10px);
    }

    .user-badge.super-admin {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    .user-badge.admin {
      background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }

    .mobile-menu-toggle {
      display: none;
      background: rgba(255, 255, 255, 0.2);
      border: none;
      color: white;
      padding: 0.5rem;
      border-radius: 0.5rem;
      cursor: pointer;
      transition: all 0.25s;
      z-index: 1001;
    }

    .mobile-menu-toggle:hover {
      background: rgba(255, 255, 255, 0.3);
    }

    .navbar-menu {
      display: flex;
      align-items: center;
    }

    .menu-content {
      display: flex;
      align-items: center;
      gap: 2rem;
    }

    .menu-items {
      display: flex;
      gap: 0.5rem;
      align-items: center;
    }

    .menu-items a {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: white;
      text-decoration: none;
      padding: 0.625rem 1rem;
      border-radius: 0.75rem;
      font-weight: 500;
      font-size: 0.9375rem;
      transition: all 0.25s;
      position: relative;
      overflow: hidden;
    }

    .menu-items a::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(255, 255, 255, 0.1);
      transform: translateX(-100%);
      transition: transform 0.25s;
    }

    .menu-items a:hover::before,
    .menu-items a.active::before {
      transform: translateX(0);
    }

    .menu-items a:hover,
    .menu-items a.active {
      background: rgba(255, 255, 255, 0.15);
      transform: translateY(-2px);
    }

    .menu-items a svg {
      width: 20px;
      height: 20px;
      stroke-width: 2;
    }

    .admin-link {
      background: rgba(240, 147, 251, 0.2) !important;
    }

    .menu-footer {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.5rem 1rem;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 0.75rem;
      backdrop-filter: blur(10px);
    }

    .user-avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 700;
      font-size: 1rem;
    }

    .user-details {
      display: flex;
      flex-direction: column;
    }

    .user-name {
      color: white;
      font-weight: 600;
      font-size: 0.875rem;
    }

    .user-email {
      color: rgba(255, 255, 255, 0.7);
      font-size: 0.75rem;
    }

    .logout-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      color: white;
      padding: 0.625rem 1.25rem;
      border-radius: 0.75rem;
      cursor: pointer;
      font-weight: 600;
      font-size: 0.9375rem;
      transition: all 0.25s;
    }

    .logout-btn:hover {
      background: rgba(255, 255, 255, 0.95);
      color: #667eea;
      transform: translateY(-2px);
    }

    .logout-btn svg {
      width: 20px;
      height: 20px;
      stroke-width: 2;
    }

    @media (max-width: 1024px) {
      .user-info {
        display: none;
      }
    }

    @media (max-width: 768px) {
      .navbar-brand h1 {
        font-size: 1.25rem;
      }

      .user-badge {
        font-size: 0.625rem;
        padding: 0.25rem 0.5rem;
      }

      .mobile-menu-toggle {
        display: block;
      }

      .navbar-menu {
        position: fixed;
        top: 0;
        right: -100%;
        width: 280px;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: right 0.3s ease-in-out;
        padding: 5rem 1.5rem 2rem;
        overflow-y: auto;
      }

      .navbar-menu.active {
        right: 0;
      }

      .menu-content {
        flex-direction: column;
        align-items: stretch;
        gap: 1.5rem;
        height: 100%;
      }

      .menu-items {
        flex-direction: column;
        gap: 0.5rem;
        flex: 1;
      }

      .menu-items a {
        width: 100%;
        padding: 0.875rem 1rem;
      }

      .menu-footer {
        flex-direction: column;
        gap: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
      }

      .user-info {
        display: flex;
        width: 100%;
      }

      .logout-btn {
        width: 100%;
        justify-content: center;
      }
    }
  `]
})
export class NavbarComponent implements OnInit {
  currentUser: User | null = null;
  mobileMenuOpen = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
  }

  getRoleDisplay(): string {
    const role = this.currentUser?.profile?.role;
    if (!role) return 'User';
    const roleMap: { [key: number]: string } = {
      1: 'Super Admin',
      2: 'Admin',
      3: 'User'
    };
    return roleMap[role] || 'User';
  }

  getRoleBadgeClass(): string {
    const role = this.currentUser?.profile?.role;
    if (role === 1) return 'super-admin';
    if (role === 2) return 'admin';
    return 'user';
  }

  isSuperAdmin(): boolean {
    return this.authService.isSuperAdmin();
  }

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  toggleMobileMenu(): void {
    this.mobileMenuOpen = !this.mobileMenuOpen;
  }

  closeMobileMenu(): void {
    this.mobileMenuOpen = false;
  }

  logout(): void {
    this.closeMobileMenu();
    this.authService.logout();
  }
}
