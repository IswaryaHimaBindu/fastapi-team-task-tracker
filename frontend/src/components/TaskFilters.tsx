import { FormEvent } from 'react';

const statusOptions = ['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'BLOCKED'];
const priorityOptions = ['LOW', 'MEDIUM', 'HIGH'];

interface TaskFiltersProps {
  status: string;
  priority: string;
  assignee: string;
  onChange: (payload: { status: string; priority: string; assignee: string }) => void;
  onClear: () => void;
}

function TaskFilters({ status, priority, assignee, onChange, onClear }: TaskFiltersProps) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  return (
    <form className="filters-panel" onSubmit={handleSubmit}>
      <div className="filter-group">
        <label>
          Status
          <select value={status} onChange={(event) => onChange({ status: event.target.value, priority, assignee })}>
            <option value="">All</option>
            {statusOptions.map((value) => (
              <option key={value} value={value}>
                {value.replace('_', ' ')}
              </option>
            ))}
          </select>
        </label>

        <label>
          Priority
          <select value={priority} onChange={(event) => onChange({ status, priority: event.target.value, assignee })}>
            <option value="">All</option>
            {priorityOptions.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>

        <label>
          Assignee ID
          <input
            type="number"
            min="1"
            value={assignee}
            onChange={(event) => onChange({ status, priority, assignee: event.target.value })}
            placeholder="User ID"
          />
        </label>
      </div>

      <button type="button" className="filter-clear" onClick={onClear}>
        Clear filters
      </button>
    </form>
  );
}

export default TaskFilters;
