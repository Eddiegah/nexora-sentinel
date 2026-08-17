export type RiskLevel = "Low" | "Medium" | "High";

export interface Country {
  iso3: string;
  name: string;
  years_available: number[];
}

export interface PredictRequest {
  country_iso3: string;
  year: number;
  urban_population_pct?: number;
  rural_population_pct?: number;
  urban_growth_pct?: number;
  population_growth_pct?: number;
  water_access_pct?: number;
  sanitation_access_pct?: number;
  avg_precipitation_mm_day?: number;
  avg_temperature_c?: number;
}

export interface PredictResponse {
  country_iso3: string;
  country_name: string;
  requested_year: number;
  data_year_used: number;
  is_hypothetical: boolean;
  is_forecast: boolean;
  features_used: Record<string, number>;
  predicted_risk: RiskLevel;
  probabilities: Record<RiskLevel, number>;
  shap_contributions: Record<string, number>;
}

export interface HistoryRecord {
  id: number;
  created_at: string;
  country_iso3: string;
  country_name: string;
  requested_year: number;
  data_year_used: number;
  is_hypothetical: boolean;
  is_forecast: boolean;
  predicted_risk: RiskLevel;
  probabilities: Record<RiskLevel, number>;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  db_connected: boolean;
}

export interface OverviewEntry {
  country_iso3: string;
  country_name: string;
  year: number;
  is_forecast: boolean;
  predicted_risk: RiskLevel;
  probabilities: Record<RiskLevel, number>;
}

export interface TrendPoint {
  year: number;
  predicted_risk: RiskLevel;
  probabilities: Record<RiskLevel, number>;
}

export interface SubscribeResponse {
  message: string;
  country_name: string;
}
