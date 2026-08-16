import type { PredictResponse, RiskLevel } from "@/lib/types";
import RiskBadge from "./RiskBadge";

const RISK_ORDER: RiskLevel[] = ["Low", "Medium", "High"];
const BAR_COLOR: Record<RiskLevel, string> = {
  Low: "bg-emerald-500",
  Medium: "bg-amber-500",
  High: "bg-rose-500",
};

const FEATURE_LABELS: Record<string, string> = {
  country: "Country",
  year: "Year",
  urban_population_pct: "Urban population %",
  rural_population_pct: "Rural population %",
  urban_growth_pct: "Urban growth %",
  population_growth_pct: "Population growth %",
  water_access_pct: "Water access %",
  sanitation_access_pct: "Sanitation access %",
};

export default function PredictionResult({ result }: { result: PredictResponse }) {
  const shapEntries = Object.entries(result.shap_contributions).sort(
    (a, b) => Math.abs(b[1]) - Math.abs(a[1]),
  );
  const maxAbsShap = Math.max(...shapEntries.map(([, v]) => Math.abs(v)), 0.001);

  return (
    <div className="space-y-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">
            {result.country_name} &mdash; {result.requested_year}
          </h3>
          {result.data_year_used !== result.requested_year && (
            <p className="text-xs text-slate-500">
              No data for {result.requested_year}; using nearest available year ({result.data_year_used}).
            </p>
          )}
          {result.is_hypothetical && (
            <p className="text-xs font-medium text-blue-600">What-if scenario (some inputs overridden)</p>
          )}
        </div>
        <RiskBadge level={result.predicted_risk} size="lg" />
      </div>

      <div>
        <h4 className="mb-2 text-sm font-medium text-slate-700">Class probabilities</h4>
        <div className="space-y-2">
          {RISK_ORDER.map((level) => {
            const p = result.probabilities[level] ?? 0;
            return (
              <div key={level} className="flex items-center gap-3">
                <span className="w-16 text-xs font-medium text-slate-600">{level}</span>
                <div className="h-3 flex-1 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className={`h-full ${BAR_COLOR[level]} transition-all`}
                    style={{ width: `${(p * 100).toFixed(1)}%` }}
                  />
                </div>
                <span className="w-14 text-right text-xs tabular-nums text-slate-500">
                  {(p * 100).toFixed(1)}%
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <h4 className="mb-2 text-sm font-medium text-slate-700">
          Why? SHAP feature contributions for &ldquo;{result.predicted_risk}&rdquo;
        </h4>
        <div className="space-y-1.5">
          {shapEntries.map(([feature, value]) => {
            const widthPct = (Math.abs(value) / maxAbsShap) * 50;
            const positive = value >= 0;
            return (
              <div key={feature} className="flex items-center gap-2 text-xs">
                <span className="w-32 shrink-0 text-slate-600">{FEATURE_LABELS[feature] ?? feature}</span>
                <div className="relative h-3 flex-1 bg-slate-50">
                  <div className="absolute left-1/2 top-0 h-full w-px bg-slate-300" />
                  <div
                    className={`absolute top-0 h-full ${positive ? "bg-rose-400" : "bg-blue-400"}`}
                    style={
                      positive
                        ? { left: "50%", width: `${widthPct}%` }
                        : { right: "50%", width: `${widthPct}%` }
                    }
                  />
                </div>
                <span className="w-14 text-right tabular-nums text-slate-500">{value.toFixed(2)}</span>
              </div>
            );
          })}
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Red bars push toward the predicted class; blue bars push away from it.
        </p>
      </div>
    </div>
  );
}
