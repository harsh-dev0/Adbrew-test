import { useState } from 'react';

export const TodoForm = ({ onSubmit, loading }) => {
  const [description, setDescription] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!description.trim()) {
      return;
    }

    try {
      await onSubmit(description);
      setDescription('');
    } catch (error) {
      console.error('Failed to create todo:', error);
    }
  };

  return (
    <div className="create-section">
      <h2>Create a Todo</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="todo">Todo Description:</label>
          <input
            type="text"
            id="todo"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter your todo..."
            disabled={loading}
            maxLength={500}
          />
        </div>
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Adding...' : 'Add Todo'}
        </button>
      </form>
    </div>
  );
};
