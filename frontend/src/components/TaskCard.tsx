import { Task } from '../types';

function TaskCard({ task }: { task: Task }) {
  return (
    <article className="task-card">
      <div className="task-card__header">
        <h2>{task.title}</h2>
        <span className="badge">{task.status}</span>
      </div>

      <p>{task.description}</p>

      <div className="task-card__meta">
        <span>Priority: {task.priority}</span>
        {task.due_date && <span>Due: {task.due_date}</span>}
        {task.completed_at && <span>Completed: {new Date(task.completed_at).toLocaleDateString()}</span>}
      </div>
    </article>
  );
}

export default TaskCard;
