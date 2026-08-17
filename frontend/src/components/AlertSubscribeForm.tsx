"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { Country } from "@/lib/types";

export default function AlertSubscribeForm({ countries }: { countries: Country[] }) {
  const [email, setEmail] = useState("");
  const [countryIso3, setCountryIso3] = useState(countries[0]?.iso3 ?? "");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [message, setMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");
    try {
      const res = await api.subscribe(email, countryIso3);
      setMessage(res.message);
      setStatus("done");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  }

  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-stone-900">Get notified of High risk</h3>
      <p className="mt-1 text-sm text-stone-500">
        Subscribe to an email alert if a country&apos;s predicted risk reaches High. Checked once daily
        against real, current predictions.
      </p>

      {status === "done" ? (
        <p className="mt-4 rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</p>
      ) : (
        <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="flex-1">
            <span className="mb-1 block text-xs font-medium text-stone-600">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </label>
          <label className="sm:w-56">
            <span className="mb-1 block text-xs font-medium text-stone-600">Country</span>
            <select
              value={countryIso3}
              onChange={(e) => setCountryIso3(e.target.value)}
              className="w-full rounded-lg border border-stone-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              {countries.map((c) => (
                <option key={c.iso3} value={c.iso3}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <button
            type="submit"
            disabled={status === "loading" || !email || !countryIso3}
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {status === "loading" ? "Subscribing..." : "Subscribe"}
          </button>
        </form>
      )}

      {status === "error" && <p className="mt-3 text-sm text-rose-600">{message}</p>}
    </div>
  );
}
