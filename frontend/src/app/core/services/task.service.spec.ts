import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TaskService } from './task.service';
import { Task, PaginatedResponse } from '../models/task.model';

describe('TaskService', () => {
  let service: TaskService;
  let httpMock: HttpTestingController;
  const API_URL = 'http://localhost:8000/api';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [TaskService]
    });
    service = TestBed.inject(TaskService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getTasks', () => {
    it('should retrieve tasks with pagination', () => {
      const mockResponse: PaginatedResponse<Task> = {
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            title: 'Test Task 1',
            description: 'Description 1',
            status: 'TODO',
            priority: 'HIGH',
            due_date: '2026-02-20',
            completed: false,
            created_at: '2026-02-19T10:00:00Z',
            updated_at: '2026-02-19T10:00:00Z',
            created_by: 1,
            created_by_username: 'testuser',
            created_by_role: 3,
            created_by_role_display: 'User'
          },
          {
            id: 2,
            title: 'Test Task 2',
            description: 'Description 2',
            status: 'IN_PROGRESS',
            priority: 'MEDIUM',
            due_date: '2026-02-21',
            completed: false,
            created_at: '2026-02-19T11:00:00Z',
            updated_at: '2026-02-19T11:00:00Z',
            created_by: 1,
            created_by_username: 'testuser',
            created_by_role: 3,
            created_by_role_display: 'User'
          }
        ]
      };

      service.getTasks({}).subscribe(response => {
        expect(response.count).toBe(2);
        expect(response.results.length).toBe(2);
        expect(response.results[0].title).toBe('Test Task 1');
      });

      const req = httpMock.expectOne(`${API_URL}/tasks/`);
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });

    it('should handle query parameters', () => {
      const mockResponse: PaginatedResponse<Task> = {
        count: 1,
        next: null,
        previous: null,
        results: []
      };

      service.getTasks({ status: 'DONE', priority: 'HIGH' }).subscribe();

      const req = httpMock.expectOne(
        req => req.url === `${API_URL}/tasks/` && 
               req.params.get('status') === 'DONE' &&
               req.params.get('priority') === 'HIGH'
      );
      expect(req.request.method).toBe('GET');
      req.flush(mockResponse);
    });
  });

  describe('getTask', () => {
    it('should retrieve a single task by id', () => {
      const mockTask: Task = {
        id: 1,
        title: 'Test Task',
        description: 'Test Description',
        status: 'TODO',
        priority: 'HIGH',
        due_date: '2026-02-20',
        completed: false,
        created_at: '2026-02-19T10:00:00Z',
        updated_at: '2026-02-19T10:00:00Z',
        created_by: 1,
        created_by_username: 'testuser',
        created_by_role: 3,
        created_by_role_display: 'User'
      };

      service.getTask(1).subscribe(task => {
        expect(task).toEqual(mockTask);
      });

      const req = httpMock.expectOne(`${API_URL}/tasks/1/`);
      expect(req.request.method).toBe('GET');
      req.flush(mockTask);
    });
  });

  describe('createTask', () => {
    it('should create a new task', () => {
      const newTask: Partial<Task> = {
        title: 'New Task',
        description: 'New Description',
        status: 'TODO',
        priority: 'MEDIUM',
        due_date: '2026-02-22'
      };

      const mockResponse: Task = {
        id: 3,
        ...newTask,
        completed: false,
        created_at: '2026-02-19T12:00:00Z',
        updated_at: '2026-02-19T12:00:00Z',
        created_by: 1,
        created_by_username: 'testuser',
        created_by_role: 3,
        created_by_role_display: 'User'
      } as Task;

      service.createTask(newTask).subscribe(task => {
        expect(task.id).toBe(3);
        expect(task.title).toBe('New Task');
      });

      const req = httpMock.expectOne(`${API_URL}/tasks/`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newTask);
      req.flush(mockResponse);
    });
  });

  describe('updateTask', () => {
    it('should update an existing task', () => {
      const updatedTask: Partial<Task> = {
        id: 1,
        title: 'Updated Task',
        description: 'Updated Description'
      };

      const mockResponse: Task = {
        ...updatedTask,
        status: 'TODO',
        priority: 'HIGH',
        due_date: '2026-02-20',
        completed: false,
        created_at: '2026-02-19T10:00:00Z',
        updated_at: '2026-02-19T13:00:00Z',
        created_by: 1,
        created_by_username: 'testuser',
        created_by_role: 3,
        created_by_role_display: 'User'
      } as Task;

      service.updateTask(1, updatedTask).subscribe(task => {
        expect(task.title).toBe('Updated Task');
      });

      const req = httpMock.expectOne(`${API_URL}/tasks/1/`);
      expect(req.request.method).toBe('PUT');
      req.flush(mockResponse);
    });
  });

  describe('deleteTask', () => {
    it('should delete a task', () => {
      service.deleteTask(1).subscribe(response => {
        expect(response).toBeTruthy();
      });

      const req = httpMock.expectOne(`${API_URL}/tasks/1/`);
      expect(req.request.method).toBe('DELETE');
      req.flush({});
    });
  });

  describe('completeTask', () => {
    it('should mark task as complete', () => {
      const mockResponse: Task = {
        id: 1,
        title: 'Test Task',
        description: 'Test Description',
        status: 'DONE',
        priority: 'HIGH',
        due_date: '2026-02-20',
        completed: true,
        created_at: '2026-02-19T10:00:00Z',
        updated_at: '2026-02-19T14:00:00Z',
        created_by: 1,
        created_by_username: 'testuser',
        created_by_role: 3,
        created_by_role_display: 'User'
      };

      service.completeTask(1).subscribe(task => {
        expect(task.completed).toBe(true);
        expect(task.status).toBe('DONE');
      });

      const req = httpMock.expectOne(`${API_URL}/tasks/1/complete/`);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
    });
  });

  describe('uncompleteTask', () => {
    it('should mark task as incomplete', () => {
      const mockResponse: Task = {
        id: 1,
        title: 'Test Task',
        description: 'Test Description',
        status: 'TODO',
        priority: 'HIGH',
        due_date: '2026-02-20',
        completed: false,
        created_at: '2026-02-19T10:00:00Z',
        updated_at: '2026-02-19T15:00:00Z',
        created_by: 1,
        created_by_username: 'testuser',
        created_by_role: 3,
        created_by_role_display: 'User'
      };

      service.uncompleteTask(1).subscribe(task => {
        expect(task.completed).toBe(false);
      });

      const req = httpMock.expectOne(`${API_URL}/tasks/1/uncomplete/`);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
    });
  });
});
