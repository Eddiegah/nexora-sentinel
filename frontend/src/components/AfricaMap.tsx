"use client";

import { useEffect, useMemo, useState } from "react";
import { geoMercator, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { Feature, Geometry } from "geojson";
import type { OverviewEntry, RiskLevel } from "@/lib/types";
import { NUMERIC_TO_ISO3 } from "@/lib/africaIso";

const RISK_FILL: Record<RiskLevel, string> = {
  Low: "#10b981",
  Medium: "#f59e0b",
  High: "#e11d48",
};

const TOPOJSON_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json";
const WIDTH = 760;
const HEIGHT = 700;

type CountryFeature = Feature<Geometry, { name: string }>;

export default function AfricaMap({
  entries,
  onSelectCountry,
}: {
  entries: OverviewEntry[];
  onSelectCountry?: (iso3: string) => void;
}) {
  const [world, setWorld] = useState<CountryFeature[] | null>(null);
  const [hovered, setHovered] = useState<{ iso3: string; x: number; y: number } | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(TOPOJSON_URL)
      .then((r) => r.json())
      .then((topo: Topology) => {
        if (cancelled) return;
        const geoms = topo.objects.countries as GeometryCollection;
        const collection = feature(topo, geoms);
        const features = ("features" in collection ? collection.features : [collection]) as CountryFeature[];
        setWorld(features);
      })
      .catch(() => setWorld([]));
    return () => {
      cancelled = true;
    };
  }, []);

  const entryByIso3 = useMemo(() => new Map(entries.map((e) => [e.country_iso3, e])), [entries]);

  const { africaFeatures, restFeatures, path } = useMemo(() => {
    if (!world) return { africaFeatures: [], restFeatures: [], path: null };

    const africa: CountryFeature[] = [];
    const rest: CountryFeature[] = [];
    for (const f of world) {
      const id = String((f as unknown as { id?: string | number }).id ?? "");
      if (NUMERIC_TO_ISO3[id]) africa.push(f);
      else rest.push(f);
    }

    const projection = geoMercator().fitExtent(
      [
        [20, 20],
        [WIDTH - 20, HEIGHT - 20],
      ],
      { type: "FeatureCollection", features: africa },
    );
    const pathGen = geoPath(projection);
    return { africaFeatures: africa, restFeatures: rest, path: pathGen };
  }, [world]);

  if (world === null) {
    return (
      <div className="flex h-[500px] items-center justify-center rounded-2xl border border-stone-200 bg-white">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-stone-200 border-t-brand-600" />
      </div>
    );
  }

  return (
    <div className="relative rounded-2xl border border-stone-200 bg-white p-2 shadow-sm">
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full" role="img" aria-label="Map of Africa colored by predicted malaria risk">
        <g>
          {restFeatures.map((f, i) => (
            <path key={i} d={path?.(f) ?? undefined} fill="#f5f5f4" stroke="#e7e5e4" strokeWidth={0.5} />
          ))}
        </g>
        <g>
          {africaFeatures.map((f) => {
            const id = String((f as unknown as { id?: string | number }).id ?? "");
            const iso3 = NUMERIC_TO_ISO3[id];
            const entry = entryByIso3.get(iso3);
            const d = path?.(f) ?? undefined;
            const baseOpacity = entry ? 0.5 + entry.probabilities[entry.predicted_risk] * 0.5 : 1;
            const isHovered = hovered?.iso3 === iso3;
            return (
              <path
                key={id}
                d={d}
                fill={entry ? RISK_FILL[entry.predicted_risk] : "#d6d3d1"}
                fillOpacity={isHovered ? 1 : baseOpacity}
                stroke="#ffffff"
                strokeWidth={1}
                style={{ transition: "fill-opacity 150ms" }}
                className="cursor-pointer"
                onMouseMove={(e) => {
                  const rect = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
                  setHovered({ iso3, x: e.clientX - rect.left, y: e.clientY - rect.top });
                }}
                onMouseLeave={() => setHovered(null)}
                onClick={() => entry && onSelectCountry?.(iso3)}
              />
            );
          })}
        </g>
      </svg>

      {hovered && entryByIso3.get(hovered.iso3) && (
        <div
          className="pointer-events-none absolute z-10 rounded-lg bg-stone-900 px-3 py-2 text-xs text-white shadow-xl"
          style={{ left: hovered.x + 12, top: hovered.y + 12 }}
        >
          <div className="font-semibold">{entryByIso3.get(hovered.iso3)?.country_name}</div>
          <div className="mt-0.5 text-stone-300">
            {entryByIso3.get(hovered.iso3)?.predicted_risk} risk &middot;{" "}
            {((entryByIso3.get(hovered.iso3)?.probabilities[entryByIso3.get(hovered.iso3)!.predicted_risk] ?? 0) * 100).toFixed(0)}%
            confidence
          </div>
        </div>
      )}

      <div className="flex items-center justify-center gap-4 pb-2 pt-1 text-xs text-stone-500">
        {(["Low", "Medium", "High"] as RiskLevel[]).map((r) => (
          <span key={r} className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: RISK_FILL[r] }} />
            {r}
          </span>
        ))}
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-stone-300" />
          No data
        </span>
      </div>
    </div>
  );
}
