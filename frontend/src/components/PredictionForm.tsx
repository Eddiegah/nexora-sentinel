"use client";

import { useMemo, useState } from "react";
import type { Country, PredictRequest } from "@/lib/types";

// Matches the backend's FORECAST_MAX_HORIZON in data_lookup.py.
const FORECAST_MAX_HORIZON = 6;

const OVERRIDE_FIELDS: { key: keyof PredictRequest; label: string }[] = [
  { key: "urban_population_pct", label: "Urban population (%)" },
  { key: "rural_population_pct", label: "Rural population (%)" },
  { key: "urban_growth_pct", label: "Urban growth (%/yr)" },
  { key: "population_growth_pct", label: "Population growth (%/yr)" },
  { key: "water_access_pct", label: "Basic water access (%)" },
  { key: "sanitation_access_pct", label: "Basic sanitation access (%)" },
  { key: "avg_precipitation_mm_day", label: "Avg precipitation (mm/day)" },
  { key: "avg_temperature_c", label: "Avg temperature (°C)" },
];

export default function PredictionForm({
  countries,
  onSubmit,
  loading,
}: {
  countries: Country[];
  onSubmit: (req: PredictRequest) => void;
  loading: boolean;
}) {
  const [countryIso3, setCountryIso3] = useState(countries[0]?.iso3 ?? "");
  const [year, setYear] = useState(countries[0]?.years_available.at(-1) ?? 2024);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [overrides, setOverrides] = useState<Partial<Record<string, number>>>({});

  const selectedCountry = useMemo(
    () => countries.find((c) => c.iso3 === countryIso3),
    [countries, countryIso3],
  );

  const yearOptions = useMemo(() => {
    const real = selectedCountry?.years_available ?? [];
    if (real.length === 0) return [];
    const lastReal = real[real.length - 1];
    const forecastYears = Array.from({ length: FORECAST_MAX_HORIZON }, (_, i) => lastReal + i + 1);
    return [...real.map((y) => ({ year: y, forecast: false })), ...forecastYears.map((y) => ({ year: y, forecast: true }))];
  }, [selectedCountry]);

  function handleCountryChange(iso3: string) {
    setCountryIso3(iso3);
    const c = countries.find((x) => x.iso3 === iso3);
    if (c) setYear(c.years_available.at(-1) ?? year);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const cleanOverrides = Object.fromEntries(
      Object.entries(overrides).filter(([, v]) => v !== undefined && v !== null && !Number.isNaN(v)),
    );
    onSubmit({ country_iso3: countryIso3, year, ...cleanOverrides });
  }

  const inputClass =
    "w-full rounded-lg border border-stone-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500";

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="mb-1 block text-sm font-medium text-stone-700">Country</span>
          <select value={countryIso3} onChange={(e) => handleCountryChange(e.target.value)} className={inputClass}>
            {countries.map((c) => (
              <option key={c.iso3} value={c.iso3}>
                {c.name}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium text-stone-700">Year</span>
          <select value={year} onChange={(e) => setYear(Number(e.target.value))} className={inputClass}>
            {yearOptions.map(({ year: y, forecast }) => (
              <option key={y} value={y}>
                {y}
                {forecast ? " (forecast)" : ""}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        type="button"
        onClick={() => setShowAdvanced((v) => !v)}
        className="text-sm font-medium text-brand-600 hover:underline"
      >
        {showAdvanced ? "Hide" : "Show"} what-if overrides
      </button>

      {showAdvanced && (
        <div className="grid grid-cols-1 gap-3 rounded-xl bg-stone-50 p-4 sm:grid-cols-2">
          <p className="col-span-full text-xs text-stone-500">
            Leave blank to use the real recorded value for this country/year. Fill in a value to see how the
            prediction changes under a hypothetical scenario.
          </p>
          {OVERRIDE_FIELDS.map(({ key, label }) => (
            <label key={key} className="block">
              <span className="mb-1 block text-xs font-medium text-stone-600">{label}</span>
              <input
                type="number"
                step="0.1"
                placeholder="auto"
                value={overrides[key] ?? ""}
                onChange={(e) =>
                  setOverrides((prev) => ({
                    ...prev,
                    [key]: e.target.value === "" ? undefined : Number(e.target.value),
                  }))
                }
                className={`${inputClass} py-1.5`}
              />
            </label>
          ))}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !countryIso3}
        className="w-full rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? (
          <span className="inline-flex items-center gap-2">
            <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/40 border-t-white" />
            Predicting...
          </span>
        ) : (
          "Predict Outbreak Risk"
        )}
      </button>
    </form>
  );
}
