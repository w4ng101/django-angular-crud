export interface Task {
  id?: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  created_by?: number;
  created_by_username?: string;
  created_by_email?: string;
  created_by_role?: number;
  created_by_role_display?: string;
  created_at?: string;
  updated_at?: string;
  due_date?: string | null;
  completed: boolean;
}

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'DONE';
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH';

export interface TaskStatistics {
  total: number;
  completed: number;
  todo: number;
  in_progress: number;
  done: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
