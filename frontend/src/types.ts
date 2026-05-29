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
