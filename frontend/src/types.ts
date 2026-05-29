export interface Task {
  id: number;
  title: string;
  description?: string | null;
  status: string;
  priority: string;
  assignee_id?: number | null;
  due_date?: string | null;
  completed_at?: string | null;
}

export interface TaskPage {
  items: Task[];
  total: number;
  page: number;
  limit: number;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
}
