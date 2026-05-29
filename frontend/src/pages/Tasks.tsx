import { useCallback, useEffect, useMemo, useState } from 'react';
import api from '../api/axios';
import TaskBoard from '../components/TaskBoard';
import TaskFilters from '../components/TaskFilters';
import Pagination from '../components/Pagination';
import Notifications from '../components/Notifications';
import useWebsocket from '../hooks/useWebsocket';
import { useAuth } from '../contexts/AuthContext';
import { getUserIdFromToken } from '../utils/jwt';
import { NotificationItem, Task, TaskPage } from '../types';

const PAGE_SIZE = 20;

function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({ status: '', priority: '', assignee: '' });
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const { token } = useAuth();
  const userId = useMemo(() => (token ? getUserIdFromToken(token) : null), [token]);

  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params: Record<string, string | number> = {
        page,
        limit: PAGE_SIZE,
      };

      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      if (filters.assignee) params.assignee_id = Number(filters.assignee);

      const response = await api.get('/tasks', { params });
      const data = response.data.data as TaskPage;
      setTasks(data.items ?? []);
      setTotal(data.total ?? 0);
    } catch (err) {
      setError('Unable to load tasks.');
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  useWebsocket({
    userId,
    onMessage: (event) => {
      try {
        const payload = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        const notification: NotificationItem = {
          id: `${Date.now()}-${payload.event}`,
          title: payload.event ?? 'Task update',
          message: payload.message ?? 'You have a task notification.',
        };
        setNotifications((current) => [notification, ...current]);
      } catch {
        console.warn('Could not parse websocket message');
      }
    },
  });

  useEffect(() => {
    if (!notifications.length) return;
    const timer = window.setTimeout(() => {
      setNotifications((current) => current.slice(0, Math.max(current.length - 1, 0)));
    }, 6000);

    return () => window.clearTimeout(timer);
  }, [notifications]);

  const handleFilterChange = (payload: { status: string; priority: string; assignee: string }) => {
    setFilters(payload);
    setPage(1);
  };

  const handleClearFilters = () => {
    setFilters({ status: '', priority: '', assignee: '' });
    setPage(1);
  };

  return (
    <main className="page-container">
      <section className="page-header">
        <h1>Task Board</h1>
        <p>Organize tasks by workflow stage and track progress across the team.</p>
      </section>

      <TaskFilters
        status={filters.status}
        priority={filters.priority}
        assignee={filters.assignee}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      <Notifications notifications={notifications} />

      {loading && <p>Loading tasks…</p>}
      {error && <p className="error-text">{error}</p>}
      {!loading && tasks.length === 0 && <p>No tasks available.</p>}

      {!loading && tasks.length > 0 && <TaskBoard tasks={tasks} />}

      <Pagination page={page} total={total} limit={PAGE_SIZE} onPageChange={setPage} />
    </main>
  );
}

export default Tasks;
