import axios from 'axios';
import { API_URL } from './config';
import { store } from '../store';
import { refreshThunk, logoutThunk } from '../store/slices/authSlice';
import { getTokens } from '../auth/tokenService';

export const api = axios.create({
  baseURL: API_URL
});

// Interceptor request: injeta accessToken
api.interceptors.request.use(
  async (config) => {
    const { accessToken } = await getTokens();
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor response: se 401, tenta refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error?.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        await store.dispatch(refreshThunk()).unwrap();
        const { accessToken } = await getTokens();
        if (accessToken && originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        }
        return api(originalRequest);
      } catch (refreshErr) {
        await store.dispatch(logoutThunk());
        return Promise.reject(refreshErr);
      }
    }
    return Promise.reject(error);
  }
);
