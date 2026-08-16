import type { RiskLevel } from "@/lib/types";

const STYLES: Record<RiskLevel, string> = {
  Low: "bg-emerald-100 text-emerald-800 border-emerald-300",
  Medium: "bg-amber-100 text-amber-800 border-amber-300",
  High: "bg-rose-100 text-rose-800 border-rose-300",
};

export default function RiskBadge({ level, size = "md" }: { level: RiskLevel; size?: "sm" | "md" | "lg" }) {
  const sizeClass = size === "lg" ? "text-lg px-4 py-1.5" : size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-3 py-1";
  return (
    <span className={`inline-flex items-center rounded-full border font-semibold ${STYLES[level]} ${sizeClass}`}>
      {level} Risk
    </span>
  );
}
