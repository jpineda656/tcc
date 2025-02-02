// frontend/src/services/api.js
import axios from 'axios';
import { useAuthStore } from '@/store/auth';
import router from '@/router';

axios.defaults.baseURL = 'http://localhost:8000';

// Interceptor de request
axios.interceptors.request.use(config => {
  const authStore = useAuthStore();
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
}, error => Promise.reject(error));

// Interceptor de response
axios.interceptors.response.use(response => response,
  (error) => {
    const authStore = useAuthStore();
    if (error.response && error.response.status === 401) {
      // Manejo del token expirado
      authStore.logout();
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

export default axios; // Exporta axios ya configurado
