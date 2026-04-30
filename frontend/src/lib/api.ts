import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true, // send httpOnly cookies on every request
});

// On 401, attempt token refresh then retry the original request
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;
    
    // Don't redirect if we are already trying to refresh or check current user
    const skipRedirect = 
      originalRequest.url?.includes("/api/v1/auth/me") || 
      originalRequest.url?.includes("/api/v1/auth/refresh");

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        await axios.post(
          `${import.meta.env.VITE_API_URL}/api/v1/auth/refresh`,
          {},
          { withCredentials: true },
        );
        return api(originalRequest);
      } catch (refreshError) {
        if (!skipRedirect) {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);

export default api;
