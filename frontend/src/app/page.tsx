"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Country, HealthResponse, HistoryRecord, PredictRequest, PredictResponse } from "@/lib/types";
import PredictionForm from "@/components/PredictionForm";
import PredictionResult from "@/components/PredictionResult";
import HistoryTable from "@/components/HistoryTable";

export default function Home() {
  const [countries, setCountries] = useState<Country[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initError, setInitError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
    api
      .getCountries()
      .then(setCountries)
      .catch((e) => setInitError(e.message));
    api
      .getHistory()
      .then(setHistory)
      .catch(() => {});
  }, []);

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

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-4xl px-6 py-6">
          <h1 className="text-2xl font-bold tracking-tight">Nexora Sentinel</h1>
          <p className="mt-1 text-sm text-slate-500">
            Malaria outbreak risk prediction for Africa &mdash; trained on real WHO &amp; World Bank data.
          </p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <StatusPill ok={health?.status === "ok"} label="API" />
            <StatusPill ok={!!health?.model_loaded} label="Model" />
            <StatusPill ok={!!health?.db_connected} label="History DB" />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl space-y-8 px-6 py-8">
        {initError && (
          <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            Could not reach the API ({initError}). Make sure the backend is running.
          </div>
        )}

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
      </main>

      <footer className="mx-auto max-w-4xl px-6 py-8 text-xs text-slate-400">
        Model: XGBoost, temporal holdout accuracy 81.0% (2020&ndash;2024 held out). Risk tertiles computed from
        this dataset&apos;s own malaria incidence distribution &mdash; see docs/methodology.json.
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
