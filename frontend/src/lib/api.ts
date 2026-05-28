/**
 * Tiny axios wrapper so every component talks to the backend
 * through a single configured client.
 *
 * Usage:
 *   import { api } from "@/lib/api";
 *   const { data } = await api.get("/api/health");
 */
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  withCredentials: false,
  headers: { "Content-Type": "application/json" },
});

// In Phase 6 we'll attach the JWT here automatically.
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
