import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { TaskService } from '../../../core/services/task.service';
import { Task } from '../../../core/models/task.model';

@Component({
  selector: 'app-task-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NavbarComponent],
  templateUrl: './task-form.component.html',
  styleUrls: ['./task-form.component.css']
})
export class TaskFormComponent implements OnInit {
  taskForm!: FormGroup;
  loading = false;
  errorMessage = '';
  isEditMode = false;
  taskId: number | null = null;

  statusOptions = [
    { value: 'TODO', label: 'To Do' },
    { value: 'IN_PROGRESS', label: 'In Progress' },
    { value: 'DONE', label: 'Done' }
  ];

  priorityOptions = [
    { value: 'LOW', label: 'Low' },
    { value: 'MEDIUM', label: 'Medium' },
    { value: 'HIGH', label: 'High' }
  ];

  constructor(
    private fb: FormBuilder,
    private taskService: TaskService,
    private router: Router,
    private route: ActivatedRoute,
    private toastr: ToastrService
  ) {}

  ngOnInit(): void {
    this.taskForm = this.fb.group({
      title: ['', [Validators.required]],
      description: [''],
      status: ['TODO', [Validators.required]],
      priority: ['MEDIUM', [Validators.required]],
      due_date: [''],
      completed: [false]
    });

    // Check if we're in edit mode
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.taskId = +id;
      this.loadTask(this.taskId);
    }
  }

  loadTask(id: number): void {
    this.loading = true;
    this.taskService.getTask(id).subscribe({
      next: (task) => {
        this.taskForm.patchValue({
          title: task.title,
          description: task.description,
          status: task.status,
          priority: task.priority,
          due_date: task.due_date || '',
          completed: task.completed
        });
        this.loading = false;
      },
      error: (error) => {
        this.errorMessage = 'Error loading task';
        this.loading = false;
        console.error(error);
      }
    });
  }

  onSubmit(): void {
    if (this.taskForm.valid) {
      this.loading = true;
      this.errorMessage = '';

      const taskData = { 
        ...this.taskForm.value,
        due_date: this.taskForm.value.due_date || null
      };

      const operation = this.isEditMode && this.taskId
        ? this.taskService.updateTask(this.taskId, taskData)
        : this.taskService.createTask(taskData);

      operation.subscribe({
        next: () => {
          if (this.isEditMode) {
            this.toastr.success('Task updated successfully!', 'Success');
          } else {
            this.toastr.success('Task created successfully!', 'Success');
          }
          this.router.navigate(['/tasks']);
        },
        error: (error) => {
          this.errorMessage = error.error?.detail || 'Error saving task';
          this.toastr.error(this.errorMessage, 'Error');
          this.loading = false;
          console.error(error);
        }
      });
    }
  }

  cancel(): void {
    this.router.navigate(['/tasks']);
  }
}
