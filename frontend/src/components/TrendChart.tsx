import type { RiskLevel, TrendPoint } from "@/lib/types";

const RISK_Y: Record<RiskLevel, number> = { Low: 2, Medium: 1, High: 0 };
const RISK_COLOR: Record<RiskLevel, string> = {
  Low: "#10b981",
  Medium: "#f59e0b",
  High: "#f43f5e",
};

const WIDTH = 720;
const HEIGHT = 220;
const PAD_X = 40;
const PAD_Y = 24;

export default function TrendChart({ points, countryName }: { points: TrendPoint[]; countryName: string }) {
  if (points.length === 0) return null;

  const sorted = [...points].sort((a, b) => a.year - b.year);
  const xStep = (WIDTH - PAD_X * 2) / Math.max(sorted.length - 1, 1);
  const yFor = (level: RiskLevel) => PAD_Y + (2 - RISK_Y[level]) * ((HEIGHT - PAD_Y * 2) / 2);
  const xFor = (i: number) => PAD_X + i * xStep;

  const linePath = sorted
    .map((p, i) => `${i === 0 ? "M" : "L"} ${xFor(i).toFixed(1)} ${yFor(p.predicted_risk).toFixed(1)}`)
    .join(" ");

  const firstYear = sorted[0].year;
  const lastYear = sorted[sorted.length - 1].year;
  const firstRisk = sorted[0].predicted_risk;
  const lastRisk = sorted[sorted.length - 1].predicted_risk;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-1 text-lg font-semibold text-slate-900">{countryName} risk trend, {firstYear}&ndash;{lastYear}</h3>
      <p className="mb-4 text-xs text-slate-500">
        Predicted risk per year using real recorded demographic and climate data for each year (not a single
        interpolated line &mdash; each point is its own model prediction).
      </p>

      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full" role="img" aria-label={`Risk trend for ${countryName}`}>
        {(["Low", "Medium", "High"] as RiskLevel[]).map((level) => (
          <g key={level}>
            <line x1={PAD_X} x2={WIDTH - PAD_X} y1={yFor(level)} y2={yFor(level)} stroke="#e2e8f0" strokeWidth={1} />
            <text x={4} y={yFor(level) + 4} className="fill-slate-400" fontSize={11}>{level}</text>
          </g>
        ))}

        <path d={linePath} fill="none" stroke="#94a3b8" strokeWidth={1.5} />

        {sorted.map((p, i) => (
          <circle
            key={p.year}
            cx={xFor(i)}
            cy={yFor(p.predicted_risk)}
            r={4}
            fill={RISK_COLOR[p.predicted_risk]}
          >
            <title>{`${p.year}: ${p.predicted_risk} (${(p.probabilities[p.predicted_risk] * 100).toFixed(1)}%)`}</title>
          </circle>
        ))}

        {sorted.map((p, i) =>
          i % 4 === 0 || i === sorted.length - 1 ? (
            <text key={p.year} x={xFor(i)} y={HEIGHT - 4} textAnchor="middle" className="fill-slate-400" fontSize={10}>
              {p.year}
            </text>
          ) : null,
        )}
      </svg>

      <p className="mt-2 text-xs text-slate-500">
        {firstYear}: <span className="font-medium">{firstRisk}</span> &rarr; {lastYear}:{" "}
        <span className="font-medium">{lastRisk}</span>
      </p>
    </div>
  );
}
