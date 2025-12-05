import { TodoItem } from './TodoItem';

export const TodoList = ({ todos, loading, onToggle, onDelete }) => {
  if (loading && todos.length === 0) {
    return <div className="loading">Loading todos...</div>;
  }

  if (todos.length === 0) {
    return <div className="empty-state">No todos yet. Create one above!</div>;
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
};
