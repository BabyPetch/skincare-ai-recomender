const API_BASE_URL = 'http://localhost:5000/api';

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