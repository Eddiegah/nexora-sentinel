"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type {
  Country,
  HealthResponse,
  HistoryRecord,
  OverviewEntry,
  PredictRequest,
  PredictResponse,
  TrendPoint,
} from "@/lib/types";
import PredictionForm from "@/components/PredictionForm";
import PredictionResult from "@/components/PredictionResult";
import HistoryTable from "@/components/HistoryTable";
import TrendChart from "@/components/TrendChart";
import OverviewGrid from "@/components/OverviewGrid";

type View = "predict" | "trend" | "overview";

export default function Home() {
  const [view, setView] = useState<View>("predict");
  const [countries, setCountries] = useState<Country[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initError, setInitError] = useState<string | null>(null);

  const [trendCountry, setTrendCountry] = useState<string>("");
  const [trendPoints, setTrendPoints] = useState<TrendPoint[] | null>(null);
  const [trendLoading, setTrendLoading] = useState(false);

  const [overview, setOverview] = useState<OverviewEntry[] | null>(null);
  const [overviewLoading, setOverviewLoading] = useState(false);

  useEffect(() => {
    api.getHealth().then(setHealth).catch(() => setHealth(null));
    api
      .getCountries()
      .then((cs) => {
        setCountries(cs);
        if (cs[0]) setTrendCountry(cs[0].iso3);
      })
      .catch((e) => setInitError(e.message));
    api.getHistory().then(setHistory).catch(() => {});
  }, []);

  useEffect(() => {
    if (view === "trend" && trendCountry) {
      setTrendLoading(true);
      api
        .getTrend(trendCountry)
        .then(setTrendPoints)
        .catch(() => setTrendPoints(null))
        .finally(() => setTrendLoading(false));
    }
  }, [view, trendCountry]);

  useEffect(() => {
    if (view === "overview" && overview === null) {
      setOverviewLoading(true);
      api
        .getOverview(2024)
        .then(setOverview)
        .catch(() => setOverview([]))
        .finally(() => setOverviewLoading(false));
    }
  }, [view, overview]);

  async function handlePredict(req: PredictRequest) {
    setLoading(true);
    setError(null);
    try {
      const res = await api.predict(req);
      setResult(res);
      const updatedHistory = await api.getHistory().catch(() => null);
      if (updatedHistory) setHistory(updatedHistory);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  const trendCountryName = countries.find((c) => c.iso3 === trendCountry)?.name ?? "";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-6 py-6">
          <h1 className="text-2xl font-bold tracking-tight">Nexora Sentinel</h1>
          <p className="mt-1 text-sm text-slate-500">
            Malaria outbreak risk prediction for Africa &mdash; trained on real WHO, World Bank &amp; NASA
            climate data.
          </p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <StatusPill ok={health?.status === "ok"} label="API" />
            <StatusPill ok={!!health?.model_loaded} label="Model" />
            <StatusPill ok={!!health?.db_connected} label="History DB" />
          </div>

          <nav className="mt-5 flex gap-1 border-b border-slate-200">
            {(["predict", "trend", "overview"] as View[]).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`rounded-t-lg px-4 py-2 text-sm font-medium capitalize transition ${
                  view === v
                    ? "border-b-2 border-blue-600 text-blue-600"
                    : "text-slate-500 hover:text-slate-800"
                }`}
              >
                {v === "predict" ? "Predict" : v === "trend" ? "Country Trend" : "Africa Overview"}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-8 px-6 py-8">
        {initError && (
          <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            Could not reach the API ({initError}). Make sure the backend is running.
          </div>
        )}

        {view === "predict" && (
          <>
            {countries.length > 0 && (
              <PredictionForm countries={countries} onSubmit={handlePredict} loading={loading} />
            )}

            {error && (
              <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {error}
              </div>
            )}

            {result && <PredictionResult result={result} />}

            <section>
              <h2 className="mb-3 text-lg font-semibold text-slate-900">Recent predictions</h2>
              <HistoryTable records={history} />
            </section>
          </>
        )}

        {view === "trend" && (
          <>
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <label className="block max-w-xs">
                <span className="mb-1 block text-sm font-medium text-slate-700">Country</span>
                <select
                  value={trendCountry}
                  onChange={(e) => setTrendCountry(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                >
                  {countries.map((c) => (
                    <option key={c.iso3} value={c.iso3}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {trendLoading && <p className="text-sm text-slate-500">Loading trend...</p>}
            {!trendLoading && trendPoints && (
              <TrendChart points={trendPoints} countryName={trendCountryName} />
            )}
          </>
        )}

        {view === "overview" && (
          <>
            {overviewLoading && <p className="text-sm text-slate-500">Loading overview for all 45 countries...</p>}
            {!overviewLoading && overview && overview.length > 0 && <OverviewGrid entries={overview} />}
          </>
        )}
      </main>

      <footer className="mx-auto max-w-5xl px-6 py-8 text-xs text-slate-400">
        Model: XGBoost with demographic + real NASA climate features, temporal holdout accuracy 81.0%
        (2020&ndash;2024 held out). Risk tertiles computed from this dataset&apos;s own malaria incidence
        distribution &mdash; see docs/methodology.json.
      </footer>
    </div>
  );
}

function StatusPill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-medium ${
        ok ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-slate-200 bg-slate-50 text-slate-500"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${ok ? "bg-emerald-500" : "bg-slate-400"}`} />
      {label}
    </span>
  );
}
