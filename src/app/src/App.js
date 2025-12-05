import { useState, useEffect } from 'react';
import './App.css';
import { todoApi } from './services/api';
import { TodoForm } from './components/TodoForm';
import { TodoList } from './components/TodoList';

export function App() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTodos = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await todoApi.getAll();
      setTodos(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  const createTodo = async (description) => {
    try {
      setLoading(true);
      setError(null);
      await todoApi.create(description);
      await fetchTodos();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const toggleTodo = async (todoId, currentStatus) => {
    try {
      setError(null);
      await todoApi.update(todoId, !currentStatus);
      await fetchTodos();
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteTodo = async (todoId) => {
    try {
      setError(null);
      await todoApi.delete(todoId);
      await fetchTodos();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1 className="title">Todo Application</h1>

        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError(null)} className="close-btn">×</button>
          </div>
        )}

        <TodoForm onSubmit={createTodo} loading={loading} />

        <div className="list-section">
          <h2>List of Todos ({todos.length})</h2>
          <TodoList 
            todos={todos} 
            loading={loading} 
            onToggle={toggleTodo} 
            onDelete={deleteTodo} 
          />
        </div>
      </div>
    </div>
  );
}

export default App;


