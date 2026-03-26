import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Task, TaskStatistics, PaginatedResponse } from '../models/task.model';

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private readonly API_URL = `${environment.apiUrl}/tasks`;

  constructor(private http: HttpClient) {}

  getTasks(params?: any): Observable<PaginatedResponse<Task>> {
    let httpParams = new HttpParams();
    
    if (params) {
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          httpParams = httpParams.set(key, params[key]);
        }
      });
    }

    return this.http.get<PaginatedResponse<Task>>(`${this.API_URL}/`, { params: httpParams });
  }

  getTask(id: number): Observable<Task> {
    return this.http.get<Task>(`${this.API_URL}/${id}/`);
  }

  createTask(task: Task): Observable<Task> {
    return this.http.post<Task>(`${this.API_URL}/`, task);
  }

  updateTask(id: number, task: Partial<Task>): Observable<Task> {
    return this.http.patch<Task>(`${this.API_URL}/${id}/`, task);
  }

  deleteTask(id: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${id}/`);
  }

  completeTask(id: number): Observable<Task> {
    return this.http.post<Task>(`${this.API_URL}/${id}/complete/`, {});
  }

  uncompleteTask(id: number): Observable<Task> {
    return this.http.post<Task>(`${this.API_URL}/${id}/uncomplete/`, {});
  }

  getStatistics(): Observable<TaskStatistics> {
    return this.http.get<TaskStatistics>(`${this.API_URL}/statistics/`);
  }

  getMyTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.API_URL}/my_tasks/`);
  }
}
