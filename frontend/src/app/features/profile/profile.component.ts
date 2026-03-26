import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { NavbarComponent } from '../../shared/components/navbar/navbar.component';
import { AuthService } from '../../core/services/auth.service';
import { User } from '../../core/models/auth.model';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NavbarComponent],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  profileForm!: FormGroup;
  currentUser: User | null = null;
  loading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private toastr: ToastrService
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    
    this.profileForm = this.fb.group({
      username: [{ value: this.currentUser?.username || '', disabled: true }],
      email: [this.currentUser?.email || '', [Validators.required, Validators.email]],
      first_name: [this.currentUser?.first_name || ''],
      last_name: [this.currentUser?.last_name || '']
    });
  }

  onSubmit(): void {
    if (this.profileForm.valid) {
      this.loading = true;
      this.errorMessage = '';

      const updateData = {
        email: this.profileForm.value.email,
        first_name: this.profileForm.value.first_name,
        last_name: this.profileForm.value.last_name
      };

      this.authService.updateProfile(updateData).subscribe({
        next: (user) => {
          this.currentUser = user;
          this.toastr.success('Profile updated successfully!', 'Success');
          this.loading = false;
        },
        error: (error) => {
          this.errorMessage = error.error?.email?.[0] || 'Error updating profile';
          this.toastr.error(this.errorMessage, 'Error');
          this.loading = false;
        }
      });
    }
  }
}
