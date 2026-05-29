import TaskCard from './TaskCard';
import { Task } from '../types';

const columns = [
  { key: 'TODO', label: 'To Do' },
  { key: 'IN_PROGRESS', label: 'In Progress' },
  { key: 'IN_REVIEW', label: 'In Review' },
  { key: 'DONE', label: 'Done' },
  { key: 'BLOCKED', label: 'Blocked' },
] as const;

type ColumnKey = (typeof columns)[number]['key'];

interface TaskBoardProps {
  tasks: Task[];
}

function TaskBoard({ tasks }: TaskBoardProps) {
  const groupedTasks = columns.reduce<Record<ColumnKey, Task[]>>((acc, column) => {
    acc[column.key] = tasks.filter((task) => task.status === column.key);
    return acc;
  }, {
    TODO: [],
    IN_PROGRESS: [],
    IN_REVIEW: [],
    DONE: [],
    BLOCKED: [],
  });

  return (
    <div className="board-grid">
      {columns.map((column) => (
        <section key={column.key} className="board-column">
          <div className="board-column__header">
            <h2>{column.label}</h2>
            <span>{groupedTasks[column.key].length}</span>
          </div>
          <div className="board-column__tasks">
            {groupedTasks[column.key].map((task) => (
              <TaskCard key={task.id} task={task} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

export default TaskBoard;
