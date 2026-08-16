import type { HistoryRecord } from "@/lib/types";
import RiskBadge from "./RiskBadge";

export default function HistoryTable({ records }: { records: HistoryRecord[] }) {
  if (records.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-stone-300 bg-stone-50 p-6 text-center text-sm text-stone-500">
        No predictions yet. Run one above to see it appear here.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-stone-200 bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead className="border-b border-stone-200 bg-stone-50 text-left text-xs uppercase tracking-wide text-stone-500">
          <tr>
            <th className="px-4 py-2 font-medium">Country</th>
            <th className="px-4 py-2 font-medium">Year</th>
            <th className="px-4 py-2 font-medium">Risk</th>
            <th className="px-4 py-2 font-medium">Confidence</th>
            <th className="px-4 py-2 font-medium">Type</th>
            <th className="px-4 py-2 font-medium">When</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-stone-100">
          {records.map((r) => (
            <tr key={r.id} className="transition-colors hover:bg-stone-50">
              <td className="px-4 py-2 font-medium text-stone-800">{r.country_name}</td>
              <td className="px-4 py-2 text-stone-600">{r.requested_year}</td>
              <td className="px-4 py-2">
                <RiskBadge level={r.predicted_risk} size="sm" />
              </td>
              <td className="px-4 py-2 tabular-nums text-stone-600">
                {(r.probabilities[r.predicted_risk] * 100).toFixed(1)}%
              </td>
              <td className="px-4 py-2 text-stone-500">{r.is_hypothetical ? "What-if" : "Historical"}</td>
              <td className="px-4 py-2 text-stone-400">{new Date(r.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
