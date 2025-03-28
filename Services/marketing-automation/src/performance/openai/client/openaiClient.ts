import axios from 'axios';

const openaiClient = axios.create({
  baseURL: process.env.AI_SERVICE_URL || 'http://ai-service:3005',
  headers: {
    'Content-Type': 'application/json',
  }
});

export default openaiClient;
