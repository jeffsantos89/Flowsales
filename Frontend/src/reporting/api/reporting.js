 
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',  // URL do serviço Reporting
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
  }
});

// Função para buscar relatórios
export const fetchReports = async () => {
  try {
    const response = await api.get('/reports');
    return response.data;
  } catch (error) {
    console.error('Error fetching reports', error);
    throw error;
  }
};
