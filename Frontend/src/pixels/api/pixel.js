 
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',  // URL do serviço Pixel
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
  }
});

// Função para buscar pixels
export const fetchPixels = async () => {
  try {
    const response = await api.get('/pixels');
    return response.data;
  } catch (error) {
    console.error('Error fetching pixels', error);
    throw error;
  }
};

// Função para adicionar um pixel
export const addPixel = async (platform, event) => {
  try {
    const response = await api.post('/pixels', { platform, event });
    return response.data;
  } catch (error) {
    console.error('Error adding pixel', error);
    throw error;
  }
};
