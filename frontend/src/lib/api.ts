/**
 * Tiny axios wrapper. Every component should import `api` from here so
 * there is a single configured client.
 *
 * Auth token is attached automatically from the Zustand store.
 */
import axios from "axios";
import { useAuthStore } from "@/store/authStore";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  withCredentials: false,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-logout on 401 so users aren't stuck with a stale token.
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401 && typeof window !== "undefined") {
      const path = window.location.pathname;
      // Don't auto-logout on the login/signup pages themselves
      if (!path.startsWith("/login") && !path.startsWith("/signup")) {
        useAuthStore.getState().logout();
      }
    }
    return Promise.reject(err);
  },
);
