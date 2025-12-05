export const TodoItem = ({ todo, onToggle, onDelete }) => {
  return (
    <li className={`todo-item ${todo.completed ? 'completed' : ''}`}>
      <div className="todo-content">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={() => onToggle(todo.id, todo.completed)}
          className="todo-checkbox"
        />
        <span className="todo-description">{todo.description}</span>
        <span className="todo-date">
          {new Date(todo.created_at).toLocaleDateString()}
        </span>
      </div>
      <button
        onClick={() => onDelete(todo.id)}
        className="btn-delete"
        aria-label="Delete todo"
      >
        Delete
      </button>
    </li>
  );
};
