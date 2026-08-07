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
    if (!originalRequest) return Promise.reject(error);

    const isAuthCheck =
      originalRequest.url?.includes("/api/v1/auth/me") ||
      originalRequest.url?.includes("/api/v1/auth/refresh");

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthCheck) {
      originalRequest._retry = true;
      try {
        const baseUrl = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
        await axios.post(
          `${baseUrl}/api/v1/auth/refresh`,
          {},
          { withCredentials: true },
        );
        return api(originalRequest);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);

export default api;
