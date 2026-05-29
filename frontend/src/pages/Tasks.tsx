import { useEffect, useState } from 'react';
import api from '../api/axios';
import TaskCard from '../components/TaskCard';
import { Task } from '../types';

function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadTasks = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await api.get('/tasks');
        setTasks(response.data.data.items ?? []);
      } catch (err) {
        setError('Unable to load tasks.');
      } finally {
        setLoading(false);
      }
    };

    loadTasks();
  }, []);

  return (
    <main className="page-container">
      <section className="page-header">
        <h1>Tasks</h1>
        <p>View and manage your assigned tasks.</p>
      </section>

      {loading && <p>Loading tasks…</p>}
      {error && <p className="error-text">{error}</p>}
      {!loading && tasks.length === 0 && <p>No tasks available.</p>}

      <div className="task-grid">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </main>
  );
}

export default Tasks;
