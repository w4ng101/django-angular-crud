import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { Subject, combineLatest, Observable } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil, map, startWith } from 'rxjs/operators';
import { NavbarComponent } from '../../../shared/components/navbar/navbar.component';
import { TaskService } from '../../../core/services/task.service';
import { AuthService } from '../../../core/services/auth.service';
import { Task, PaginatedResponse } from '../../../core/models/task.model';

@Component({
  selector: 'app-task-list',
  standalone: true,
  imports: [CommonModule, RouterLink, NavbarComponent, ReactiveFormsModule],
  templateUrl: './task-list.component.html',
  styleUrls: ['./task-list.component.css']
})
export class TaskListComponent implements OnInit, OnDestroy {
  // All tasks from API
  allTasks: Task[] = [];
  // Filtered tasks to display
  filteredTasks$!: Observable<Task[]>;
  
  loading = true;
  errorMessage = '';
  
  // Reactive form controls for search and filters
  searchControl = new FormControl('');
  statusControl = new FormControl('');
  priorityControl = new FormControl('');
  
  private destroy$ = new Subject<void>();

  constructor(
    private taskService: TaskService,
    private authService: AuthService,
    private toastr: ToastrService
  ) {}

  isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  ngOnInit(): void {
    this.loadTasks();
    this.setupReactiveFilters();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadTasks(): void {
    this.loading = true;
    
    this.taskService.getTasks({}).subscribe({
      next: (response: PaginatedResponse<Task>) => {
        this.allTasks = response.results;
        this.loading = false;
      },
      error: (error) => {
        this.errorMessage = 'Error loading tasks';
        this.loading = false;
        console.error(error);
      }
    });
  }

  setupReactiveFilters(): void {
    // Combine all filter streams with RxJS
    this.filteredTasks$ = combineLatest([
      this.searchControl.valueChanges.pipe(
        startWith(''),
        debounceTime(300),
        distinctUntilChanged()
      ),
      this.statusControl.valueChanges.pipe(
        startWith('')
      ),
      this.priorityControl.valueChanges.pipe(
        startWith('')
      )
    ]).pipe(
      takeUntil(this.destroy$),
      map(([searchTerm, status, priority]) => {
        return this.filterTasks(searchTerm || '', status || '', priority || '');
      })
    );
  }

  filterTasks(searchTerm: string, status: string, priority: string): Task[] {
    let filtered = [...this.allTasks];
    
    // Search filter - search in title and description
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(task => 
        task.title.toLowerCase().includes(term) || 
        (task.description && task.description.toLowerCase().includes(term)) ||
        (task.created_by_username && task.created_by_username.toLowerCase().includes(term))
      );
    }
    
    // Status filter
    if (status) {
      filtered = filtered.filter(task => task.status === status);
    }
    
    // Priority filter
    if (priority) {
      filtered = filtered.filter(task => task.priority === priority);
    }
    
    return filtered;
  }

  clearAllFilters(): void {
    this.searchControl.setValue('');
    this.statusControl.setValue('');
    this.priorityControl.setValue('');
  }

  deleteTask(id: number | undefined): void {
    if (!id) return;
    
    if (confirm('Are you sure you want to delete this task?')) {
      this.taskService.deleteTask(id).subscribe({
        next: () => {
          this.toastr.success('Task deleted successfully!', 'Success');
          this.loadTasks();
        },
        error: (error) => {
          this.toastr.error('Error deleting task', 'Error');
          console.error(error);
        }
      });
    }
  }

  toggleComplete(task: Task): void {
    if (!task.id) return;
    
    const action = task.completed 
      ? this.taskService.uncompleteTask(task.id)
      : this.taskService.completeTask(task.id);

    action.subscribe({
      next: () => {
        const message = task.completed ? 'Task marked as incomplete' : 'Task completed successfully!';
        this.toastr.success(message, 'Success');
        this.loadTasks();
      },
      error: (error) => {
        this.toastr.error('Error updating task', 'Error');
        console.error(error);
      }
    });
  }

  getPriorityClass(priority: string): string {
    return `priority-${priority.toLowerCase()}`;
  }

  getStatusClass(status: string): string {
    return `status-${status.toLowerCase().replace('_', '-')}`;
  }
}
