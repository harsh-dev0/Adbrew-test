const API_URL = 'http://localhost:8000';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

const handleResponse = async (response) => {
  const data = await response.json();
  
  if (!data.success) {
    throw new ApiError(data.error || 'Request failed', response.status);
  }
  
  return data.data;
};

export const todoApi = {
  async getAll() {
    try {
      const response = await fetch(`${API_URL}/todos/`);
      return await handleResponse(response);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Failed to connect to server', 500);
    }
  },

  async create(description) {
    try {
      const response = await fetch(`${API_URL}/todos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: description.trim() })
      });
      return await handleResponse(response);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Failed to create todo', 500);
    }
  },

  async update(todoId, completed) {
    try {
      const response = await fetch(`${API_URL}/todos/${todoId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed })
      });
      return await handleResponse(response);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Failed to update todo', 500);
    }
  },

  async delete(todoId) {
    try {
      const response = await fetch(`${API_URL}/todos/${todoId}/`, {
        method: 'DELETE'
      });
      return await handleResponse(response);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Failed to delete todo', 500);
    }
  }
};
