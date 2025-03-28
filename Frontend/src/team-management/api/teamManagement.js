 
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',  // URL do serviço Team Management
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
  }
});

// Função para buscar equipes
export const fetchTeams = async () => {
  try {
    const response = await api.get('/teams');
    return response.data;
  } catch (error) {
    console.error('Error fetching teams', error);
    throw error;
  }
};

// Função para adicionar uma equipe
export const addTeam = async (name, description) => {
  try {
    const response = await api.post('/teams', { name, description });
    return response.data;
  } catch (error) {
    console.error('Error adding team', error);
    throw error;
  }
};
