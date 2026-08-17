import type {
  Country,
  HealthResponse,
  HistoryRecord,
  OverviewEntry,
  PredictRequest,
  PredictResponse,
  SubscribeResponse,
  TrendPoint,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function extractErrorMessage(detail: unknown): string | null {
  if (typeof detail === "string") return detail;
  // FastAPI/Pydantic validation errors are a list of {msg, loc, ...}
  if (Array.isArray(detail) && detail.length > 0 && typeof detail[0]?.msg === "string") {
    return detail[0].msg;
  }
  return null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(extractErrorMessage(body.detail) ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  getHealth: () => request<HealthResponse>("/health"),
  getCountries: () => request<Country[]>("/countries"),
  getHistory: (limit = 20) => request<HistoryRecord[]>(`/history?limit=${limit}`),
  predict: (body: PredictRequest) =>
    request<PredictResponse>("/predict", { method: "POST", body: JSON.stringify(body) }),
  getOverview: (year = 2024) => request<OverviewEntry[]>(`/overview?year=${year}`),
  getTrend: (countryIso3: string) => request<TrendPoint[]>(`/trend?country_iso3=${countryIso3}`),
  subscribe: (email: string, countryIso3: string) =>
    request<SubscribeResponse>("/alerts/subscribe", {
      method: "POST",
      body: JSON.stringify({ email, country_iso3: countryIso3 }),
    }),
};
