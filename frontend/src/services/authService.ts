import { apiClient } from "./apiClient";
import type { AuthResponse, User } from "@/types/api";

export const authService = {
  login(email: string, password: string) {
    return apiClient.post<AuthResponse>("/auth/login", { email, password });
  },
  register(payload: {
    name: string;
    email: string;
    password: string;
    village?: string;
    district?: string;
    state?: string;
  }) {
    return apiClient.post<AuthResponse>("/auth/register", payload);
  },
  logout() {
    return apiClient.post<{ success: boolean }>("/auth/logout");
  },
  me() {
    return apiClient.get<User>("/auth/me");
  },
  updateProfile(payload: Partial<User> & { farmSizeAcres?: number }) {
    return apiClient.patch<User>("/auth/me", payload);
  },
};
