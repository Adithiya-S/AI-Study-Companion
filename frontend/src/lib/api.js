/**
 * AURA Telemetry & Study Companion API Client Helper
 * 
 * In local Vite dev server (e.g. localhost:5173), defaults to backend at http://127.0.0.1:8000.
 * When served by FastAPI in production or over LAN, dynamically resolves to window.location.origin.
 */

export const API_BASE = (() => {
  if (typeof window === "undefined") return "http://127.0.0.1:8000";
  if (import.meta.env.VITE_API_BASE) return import.meta.env.VITE_API_BASE;
  const isViteDev = window.location.port === "5173" || window.location.port === "3000";
  return isViteDev ? "http://127.0.0.1:8000" : window.location.origin;
})();

export const apiUrl = (path) => {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${cleanPath}`;
};
