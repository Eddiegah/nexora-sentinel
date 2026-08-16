"use client";

import { useMemo, useState } from "react";
import type { Country, PredictRequest } from "@/lib/types";

const OVERRIDE_FIELDS: { key: keyof PredictRequest; label: string }[] = [
  { key: "urban_population_pct", label: "Urban population (%)" },
  { key: "rural_population_pct", label: "Rural population (%)" },
  { key: "urban_growth_pct", label: "Urban growth (%/yr)" },
  { key: "population_growth_pct", label: "Population growth (%/yr)" },
  { key: "water_access_pct", label: "Basic water access (%)" },
  { key: "sanitation_access_pct", label: "Basic sanitation access (%)" },
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

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className="block">
          <span className="mb-1 block text-sm font-medium text-slate-700">Country</span>
          <select
            value={countryIso3}
            onChange={(e) => handleCountryChange(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            {countries.map((c) => (
              <option key={c.iso3} value={c.iso3}>
                {c.name}
              </option>
            ))}
          </select>
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium text-slate-700">Year</span>
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            {(selectedCountry?.years_available ?? []).map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        type="button"
        onClick={() => setShowAdvanced((v) => !v)}
        className="text-sm font-medium text-blue-600 hover:underline"
      >
        {showAdvanced ? "Hide" : "Show"} what-if overrides
      </button>

      {showAdvanced && (
        <div className="grid grid-cols-1 gap-3 rounded-lg bg-slate-50 p-4 sm:grid-cols-2">
          <p className="col-span-full text-xs text-slate-500">
            Leave blank to use the real recorded value for this country/year. Fill in a value to see how the
            prediction changes under a hypothetical scenario.
          </p>
          {OVERRIDE_FIELDS.map(({ key, label }) => (
            <label key={key} className="block">
              <span className="mb-1 block text-xs font-medium text-slate-600">{label}</span>
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
                className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
              />
            </label>
          ))}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !countryIso3}
        className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Predicting..." : "Predict Outbreak Risk"}
      </button>
    </form>
  );
}
