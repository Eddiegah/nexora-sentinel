import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // "standalone" output is for the self-hosted Docker build (backend/Dockerfile
  // pattern applied to frontend/Dockerfile) -- it's incompatible with Vercel's
  // own build/packaging pipeline (missing .nft.json trace files), so it's
  // skipped when building on Vercel, which sets VERCEL=1 automatically.
  output: process.env.VERCEL ? undefined : "standalone",
};

export default nextConfig;
