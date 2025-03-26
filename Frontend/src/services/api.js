import axios from 'axios';
import { AuthContext } from '../auth/AuthProvider';
import React, { useContext, useEffect } from 'react';

export function useApi() {
  const { token, refreshToken, setToken } = useContext(AuthContext);

  const instance = axios.create({
    baseURL: process.env.REACT_APP_STORE_API_URL,
    timeout: 10000, // Configuração de tempo limite
  });

  instance.interceptors.request.use((config) => {
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }, (error) => {
    return Promise.reject(error);
  });

  instance.interceptors.response.use((response) => {
    return response;
  }, async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const newToken = await refreshToken();
      setToken(newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      return instance(originalRequest);
    }
    return Promise.reject(error);
  });

  return instance;
}

// Exemplo de uso:
import { useApi } from './services/aoi';

function MyComponent() {
  const api = useApi();

  useEffect(() => {
    api.get('/users')
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.error('Error fetching users:', error);
      });
  }, [api]);

  return <div>...</div>;
}

export default MyComponent;
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3333',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Intercepta a request e injeta o token
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token');
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepta respostas com erro (ex: 401)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
// Configurações avançadas
const CONFIG = {
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  TIMEOUT: {
    DEFAULT: 10000,
    UPLOAD: 30000,
    DOWNLOAD: 30000
  },
  CACHE_DURATION: 5 * 60 * 1000 // 5 minutes
};

// Cache manager
const cacheManager = new Map();

// Api factory com suporte a diferentes environments
export const createApi = (config = {}) => {
  const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3333',
    timeout: CONFIG.TIMEOUT.DEFAULT,
    ...config,
    headers: {
      'Content-Type': 'application/json',
      ...config.headers
    }
  });

  // Retry logic
  const retryHandler = async (error) => {
    const { config: originalConfig } = error;
    if (!originalConfig || !originalConfig._retry) {
      originalConfig._retry = 1;
      await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY));
      return instance(originalConfig);
    } else if (originalConfig._retry < CONFIG.RETRY_ATTEMPTS) {
      originalConfig._retry++;
      await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY * originalConfig._retry));
      return instance(originalConfig);
    }
    return Promise.reject(error);
  };

  // Request interceptor with enhanced error handling
  instance.interceptors.request.use(
    async (config) => {
      const token = sessionStorage.getItem('token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Cache check for GET requests
      if (config.method === 'get' && config.cache !== false) {
        const cacheKey = `${config.url}${JSON.stringify(config.params || {})}`;
        const cachedResponse = cacheManager.get(cacheKey);
        if (cachedResponse && Date.now() - cachedResponse.timestamp < CONFIG.CACHE_DURATION) {
          return Promise.resolve(cachedResponse.data);
        }
      }
      
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor with enhanced features
  instance.interceptors.response.use(
    (response) => {
      // Cache successful GET requests
      if (response.config.method === 'get' && response.config.cache !== false) {
        const cacheKey = `${response.config.url}${JSON.stringify(response.config.params || {})}`;
        cacheManager.set(cacheKey, {
          data: response,
          timestamp: Date.now()
        });
      }
      return response;
    },
    async (error) => {
      if (error.response?.status === 401) {
        sessionStorage.removeItem('token');
        window.location.href = '/login';
        return Promise.reject(error);
      }
      
      // Network errors handling
      if (!error.response && error.code === 'ECONNABORTED') {
        return retryHandler(error);
      }

      // Rate limiting handling
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'];
        await new Promise(resolve => setTimeout(resolve, (retryAfter || 1) * 1000));
        return instance(error.config);
      }

      return Promise.reject(error);
    }
  );

  return instance;
};

export default createApi();