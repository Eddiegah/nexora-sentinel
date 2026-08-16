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
import AfricaMap from "@/components/AfricaMap";
import StatCounter from "@/components/StatCounter";
import Skeleton from "@/components/Skeleton";

type View = "predict" | "trend" | "overview";

const TABS: { key: View; label: string; icon: string }[] = [
  { key: "predict", label: "Predict", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
  { key: "trend", label: "Country Trend", icon: "M3 3v18h18M7 14l4-4 4 4 5-6" },
  { key: "overview", label: "Africa Overview", icon: "M3.6 9h16.8M3.6 15h16.8M12 3a15 15 0 010 18M12 3a15 15 0 000 18" },
];

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

  function goToTrend(iso3: string) {
    setTrendCountry(iso3);
    setView("trend");
  }

  const trendCountryName = countries.find((c) => c.iso3 === trendCountry)?.name ?? "";

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900">
      {/* Hero */}
      <header className="relative overflow-hidden bg-gradient-to-br from-[#0c0a1a] via-[#151129] to-brand-900">
        <div
          className="pointer-events-none absolute -right-40 -top-40 h-96 w-96 rounded-full bg-brand-500/20 blur-3xl"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute -left-24 top-40 h-72 w-72 rounded-full bg-brand-500/10 blur-3xl"
          aria-hidden
        />

        <div className="relative mx-auto max-w-6xl px-6 pb-10 pt-14 sm:pt-16">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" className="text-brand-400">
                <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6" />
                <circle cx="12" cy="12" r="3.2" fill="currentColor" />
                <path d="M12 2v3M12 19v3M2 12h3M19 12h3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
              <span className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-100">
                Nexora Sentinel
              </span>
            </div>
            <div className="hidden gap-2 text-xs sm:flex">
              <StatusPill ok={health?.status === "ok"} label="API" />
              <StatusPill ok={!!health?.model_loaded} label="Model" />
              <StatusPill ok={!!health?.db_connected} label="History DB" />
            </div>
          </div>

          <h1 className="mt-8 max-w-2xl text-4xl font-bold leading-tight tracking-tight text-white sm:text-5xl">
            Predicting malaria outbreak risk across Africa
          </h1>
          <p className="mt-4 max-w-xl text-lg text-stone-300">
            An open, reproducible early-warning system trained on real WHO, World Bank, and NASA climate
            data &mdash; not a demo dataset, not fabricated metrics.
          </p>

          <div className="mt-12 grid grid-cols-2 gap-8 border-t border-white/10 pt-8 sm:grid-cols-4">
            <StatCounter value={45} label="Countries" />
            <StatCounter value={1101} label="Country-Year Records" />
            <StatCounter value={25} label="Years of Real Data" />
            <StatCounter value={81.0} decimals={1} suffix="%" label="Honest Model Accuracy" />
          </div>
        </div>
      </header>

      {/* Floating nav */}
      <div className="mx-auto -mt-6 max-w-6xl px-6">
        <nav className="flex gap-1 rounded-2xl border border-stone-200 bg-white p-1.5 shadow-lg shadow-stone-900/5">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setView(t.key)}
              className={`flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all ${
                view === t.key
                  ? "bg-brand-600 text-white shadow-sm"
                  : "text-stone-500 hover:bg-stone-50 hover:text-stone-800"
              }`}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d={t.icon} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      <main className="mx-auto max-w-6xl space-y-8 px-6 py-8">
        {initError && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            Could not reach the API ({initError}). Make sure the backend is running.
          </div>
        )}

        {view === "predict" && (
          <div key="predict" className="animate-fade-up space-y-8">
            {countries.length > 0 && (
              <PredictionForm countries={countries} onSubmit={handlePredict} loading={loading} />
            )}

            {error && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
                {error}
              </div>
            )}

            {result && <PredictionResult result={result} />}

            <section>
              <h2 className="mb-3 text-lg font-semibold text-stone-900">Recent predictions</h2>
              <HistoryTable records={history} />
            </section>
          </div>
        )}

        {view === "trend" && (
          <div key="trend" className="animate-fade-up space-y-8">
            <div className="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
              <label className="block max-w-xs">
                <span className="mb-1 block text-sm font-medium text-stone-700">Country</span>
                <select
                  value={trendCountry}
                  onChange={(e) => setTrendCountry(e.target.value)}
                  className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                >
                  {countries.map((c) => (
                    <option key={c.iso3} value={c.iso3}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {trendLoading && <Skeleton className="h-64 w-full" />}
            {!trendLoading && trendPoints && (
              <TrendChart points={trendPoints} countryName={trendCountryName} />
            )}
          </div>
        )}

        {view === "overview" && (
          <div key="overview" className="animate-fade-up space-y-8">
            {overviewLoading && (
              <>
                <Skeleton className="h-[500px] w-full" />
                <Skeleton className="h-40 w-full" />
              </>
            )}
            {!overviewLoading && overview && overview.length > 0 && (
              <>
                <AfricaMap entries={overview} onSelectCountry={goToTrend} />
                <p className="text-center text-xs text-stone-400">
                  Click any country to see its full risk trend, 2000&ndash;2024.
                </p>
                <OverviewGrid entries={overview} onSelectCountry={goToTrend} />
              </>
            )}
          </div>
        )}
      </main>

      <footer className="mt-8 border-t border-stone-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-8">
          <div className="grid gap-8 sm:grid-cols-3">
            <div>
              <h3 className="text-sm font-semibold text-stone-800">Data sources</h3>
              <ul className="mt-2 space-y-1 text-xs text-stone-500">
                <li>WHO Global Health Observatory</li>
                <li>World Bank Open Data</li>
                <li>NASA POWER (climate)</li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-stone-800">Model</h3>
              <p className="mt-2 text-xs text-stone-500">
                XGBoost, demographic + climate features. Temporal holdout accuracy: 81.0% (2020&ndash;2024
                held out, trained only on 2000&ndash;2019). Risk tertiles computed from this
                dataset&apos;s own distribution, not a clinical standard.
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-stone-800">Project</h3>
              <ul className="mt-2 space-y-1 text-xs text-stone-500">
                <li>
                  <a
                    href="https://github.com/Eddiegah/nexora-sentinel"
                    className="hover:text-brand-600 hover:underline"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Source code on GitHub
                  </a>
                </li>
                <li>
                  <a
                    href="https://github.com/Eddiegah/nexora-sentinel/blob/master/data/processed/methodology.json"
                    className="hover:text-brand-600 hover:underline"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Full methodology
                  </a>
                </li>
                <li>MIT License</li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function StatusPill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-medium ${
        ok ? "border-brand-400/30 bg-brand-500/10 text-brand-200" : "border-white/10 bg-white/5 text-stone-400"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${ok ? "bg-brand-400" : "bg-stone-500"}`} />
      {label}
    </span>
  );
}
