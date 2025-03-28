import axios from 'axios';

export const analyzeLoginPattern = async (data: any) => {
  const res = await axios.post('http://ai-service:3005/analyze/login-pattern', { input: data });
  return res.data;
};
