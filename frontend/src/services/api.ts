import { HealthResponse } from '../types';

export const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

export function apiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  if (!API_BASE) {
    return cleanPath.startsWith('/api/v1') ? cleanPath : `/api/v1${cleanPath}`;
  }
  const baseHasV1 = API_BASE.endsWith('/api/v1');
  const pathHasV1 = cleanPath.startsWith('/api/v1');
  if (baseHasV1 && pathHasV1) {
    return `${API_BASE}${cleanPath.substring(7)}`;
  }
  if (!baseHasV1 && !pathHasV1) {
    return `${API_BASE}/api/v1${cleanPath}`;
  }
  return `${API_BASE}${cleanPath}`;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(apiUrl('/health'));
  if (!res.ok) {
    throw new Error(`Failed to fetch health status: ${res.statusText}`);
  }
  return res.json();
}
