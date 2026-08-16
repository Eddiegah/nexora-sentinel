import type { HistoryRecord } from "@/lib/types";
import RiskBadge from "./RiskBadge";

export default function HistoryTable({ records }: { records: HistoryRecord[] }) {
  if (records.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
        No predictions yet. Run one above to see it appear here.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-2 font-medium">Country</th>
            <th className="px-4 py-2 font-medium">Year</th>
            <th className="px-4 py-2 font-medium">Risk</th>
            <th className="px-4 py-2 font-medium">Confidence</th>
            <th className="px-4 py-2 font-medium">Type</th>
            <th className="px-4 py-2 font-medium">When</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {records.map((r) => (
            <tr key={r.id}>
              <td className="px-4 py-2 font-medium text-slate-800">{r.country_name}</td>
              <td className="px-4 py-2 text-slate-600">{r.requested_year}</td>
              <td className="px-4 py-2">
                <RiskBadge level={r.predicted_risk} size="sm" />
              </td>
              <td className="px-4 py-2 tabular-nums text-slate-600">
                {(r.probabilities[r.predicted_risk] * 100).toFixed(1)}%
              </td>
              <td className="px-4 py-2 text-slate-500">{r.is_hypothetical ? "What-if" : "Historical"}</td>
              <td className="px-4 py-2 text-slate-400">{new Date(r.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
