"use client";
/**
 * Zustand store that holds the JWT and current user.
 * Persists to localStorage so the user stays logged in across reloads.
 */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface AuthUser {
  id: number;
  email: string;
  full_name: string;
  role: "user" | "admin" | string;
  created_at: string;
}

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  setSession: (token: string, user: AuthUser) => void;
  setUser: (user: AuthUser) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setSession: (token, user) => set({ token, user }),
      setUser: (user) => set({ user }),
      logout: () => set({ token: null, user: null }),
    }),
    {
      name: "ai-interview-prep-auth",
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
