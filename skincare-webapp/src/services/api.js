// src/services/api.js

const API_BASE_URL = 'http://127.0.0.1:5000/api';

export const loginUser = async (credentials) => {
  // credentials = { email, password }
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });
  return response.json();
};

export const registerUser = async (userData) => {
  // userData = { name, email, password, birthdate }
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
  return response.json();
};


export const getRecommendations = async (userProfile) => {
    const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userProfile)
    });
    
if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    
    return await response.json();
};

