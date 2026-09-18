/**
 * AURA Telemetry & Study Companion API Client Helper
 * 
 * In local Vite dev server (e.g. localhost:5173), defaults to backend at http://127.0.0.1:8000.
 * When served by FastAPI in production or over LAN, dynamically resolves to window.location.origin.
 */

export const API_BASE = (() => {
  if (typeof window === "undefined") return "http://127.0.0.1:8000";
  const envUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE;
  if (envUrl) return envUrl.replace(/\/+$/, "");
  const isViteDev = window.location.port === "5173" || window.location.port === "3000";
  return isViteDev ? "http://127.0.0.1:8000" : window.location.origin;
})();

export const apiUrl = (path) => {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${cleanPath}`;
};
