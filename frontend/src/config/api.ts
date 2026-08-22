export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

/** Backend origin (for uploaded image URLs like /uploads/xxx.jpg). */
export const BACKEND_ORIGIN = new URL(API_BASE_URL).origin;
