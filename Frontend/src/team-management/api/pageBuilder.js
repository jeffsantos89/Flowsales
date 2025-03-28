
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',  // URL do serviço Page Builder
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
  }
});

// Função para buscar páginas
export const fetchPages = async () => {
  try {
    const response = await api.get('/pages');
    return response.data;
  } catch (error) {
    console.error('Error fetching pages', error);
    throw error;
  }
};

// Função para buscar templates
export const fetchTemplates = async () => {
  try {
    const response = await api.get('/templates');
    return response.data;
  } catch (error) {
    console.error('Error fetching templates', error);
    throw error;
  }
};
