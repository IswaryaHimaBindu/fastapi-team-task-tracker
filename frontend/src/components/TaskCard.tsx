import { Task } from '../types';

function TaskCard({ task }: { task: Task }) {
  return (
    <article className="task-card">
      <div className="task-card__header">
        <div>
          <h2>{task.title}</h2>
          <p className="task-card__assignee">
            Assignee: {task.assignee_id ? `User ${task.assignee_id}` : 'Unassigned'}
          </p>
        </div>
        <span className="badge">{task.status}</span>
      </div>

      {task.description && <p>{task.description}</p>}

      <div className="task-card__meta">
        <span className="meta-chip">Priority: {task.priority}</span>
        <span className="meta-chip">
          Due: {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'N/A'}
        </span>
      </div>
    </article>
  );
}

export default TaskCard;
