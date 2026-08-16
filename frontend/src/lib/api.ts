import type {
  Country,
  HealthResponse,
  HistoryRecord,
  PredictRequest,
  PredictResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ? JSON.stringify(body.detail) : `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  getHealth: () => request<HealthResponse>("/health"),
  getCountries: () => request<Country[]>("/countries"),
  getHistory: (limit = 20) => request<HistoryRecord[]>(`/history?limit=${limit}`),
  predict: (body: PredictRequest) =>
    request<PredictResponse>("/predict", { method: "POST", body: JSON.stringify(body) }),
};
