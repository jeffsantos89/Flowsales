
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',  // URL do serviço Finance
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
  }
});

// Função para buscar planos
export const fetchPlans = async () => {
  try {
    const response = await api.get('/plans');
    return response.data;
  } catch (error) {
    console.error('Error fetching plans', error);
    throw error;
  }
};

// Função para buscar informações de cobrança
export const fetchBilling = async () => {
  try {
    const response = await api.get('/billing');
    return response.data;
  } catch (error) {
    console.error('Error fetching billing info', error);
    throw error;
  }
};
