import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5004/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * API Service for pathfinding visualization
 */

// Graph endpoints
export const fetchGraphs = async () => {
  const response = await api.get('/graphs');
  return response.data;
};

export const fetchGraph = async (graphId) => {
  const response = await api.get(`/graph/${graphId}`);
  return response.data;
};

export const validateNode = async (graphId, nodeId) => {
  try {
    const response = await api.get(`/graph/${graphId}/validate_node/${nodeId}`);
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { success: false, valid: false, error: error.message };
  }
};

export const checkReachability = async (graphId, startNode, goalNode) => {
  try {
    const response = await api.post(`/graph/${graphId}/check_reachability`, {
      start_node: startNode,
      goal_node: goalNode,
    });
    return response.data;
  } catch (error) {
    if (error.response && error.response.data) {
      return error.response.data;
    }
    return { success: false, reachable: false, error: error.message };
  }
};

// Algorithm and heuristic endpoints
export const fetchAlgorithms = async () => {
  const response = await api.get('/algorithms');
  return response.data;
};

export const fetchHeuristics = async () => {
  const response = await api.get('/heuristics');
  return response.data;
};

// Search endpoints
export const startSearch = async (searchParams) => {
  const response = await api.post('/search', searchParams);
  return response.data;
};

export const fetchSearchSteps = async (sessionId, offset = 0) => {
  const response = await api.get(`/search/${sessionId}/steps`, {
    params: { offset },
  });
  return response.data;
};

export const cancelSearch = async (sessionId) => {
  const response = await api.post(`/search/${sessionId}/cancel`);
  return response.data;
};

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;

