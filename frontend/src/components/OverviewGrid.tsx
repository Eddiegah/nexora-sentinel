import type { OverviewEntry, RiskLevel } from "@/lib/types";
import RiskBadge from "./RiskBadge";

const RISK_ORDER: Record<RiskLevel, number> = { High: 0, Medium: 1, Low: 2 };

export default function OverviewGrid({
  entries,
  onSelectCountry,
}: {
  entries: OverviewEntry[];
  onSelectCountry?: (iso3: string) => void;
}) {
  const sorted = [...entries].sort((a, b) => {
    const riskDiff = RISK_ORDER[a.predicted_risk] - RISK_ORDER[b.predicted_risk];
    if (riskDiff !== 0) return riskDiff;
    return b.probabilities[b.predicted_risk] - a.probabilities[a.predicted_risk];
  });

  const counts = entries.reduce(
    (acc, e) => ({ ...acc, [e.predicted_risk]: (acc[e.predicted_risk] ?? 0) + 1 }),
    {} as Record<RiskLevel, number>,
  );

  return (
    <div className="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-stone-900">All 45 countries</h3>
        <div className="flex gap-2 text-xs">
          <span className="rounded-full bg-rose-50 px-2 py-1 font-medium text-rose-700">{counts.High ?? 0} High</span>
          <span className="rounded-full bg-amber-50 px-2 py-1 font-medium text-amber-700">{counts.Medium ?? 0} Medium</span>
          <span className="rounded-full bg-emerald-50 px-2 py-1 font-medium text-emerald-700">{counts.Low ?? 0} Low</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
        {sorted.map((e) => (
          <button
            key={e.country_iso3}
            onClick={() => onSelectCountry?.(e.country_iso3)}
            className="flex flex-col gap-1.5 rounded-xl border border-stone-100 bg-stone-50 px-3 py-2.5 text-left transition-colors hover:border-brand-200 hover:bg-brand-50"
          >
            <span className="truncate text-sm font-medium text-stone-800" title={e.country_name}>
              {e.country_name}
            </span>
            <div className="flex items-center justify-between">
              <RiskBadge level={e.predicted_risk} size="sm" />
              <span className="text-xs tabular-nums text-stone-500">
                {(e.probabilities[e.predicted_risk] * 100).toFixed(0)}%
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
