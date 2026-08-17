import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const SITE_URL = "https://nexora-sentinel.vercel.app";
const TITLE = "Nexora Sentinel — Malaria Outbreak Risk Prediction for Africa";
const DESCRIPTION =
  "AI-powered malaria outbreak risk prediction across 45 African countries, trained on real WHO, World Bank, and NASA climate data with transparent, honestly-reported model evaluation.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: TITLE,
  description: DESCRIPTION,
  authors: [{ name: "Edmund Eric Gah", url: "https://github.com/Eddiegah" }],
  creator: "Edmund Eric Gah",
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    url: SITE_URL,
    siteName: "Nexora Sentinel",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "Nexora Sentinel",
  description: DESCRIPTION,
  url: SITE_URL,
  applicationCategory: "HealthApplication",
  operatingSystem: "Web",
  author: {
    "@type": "Person",
    name: "Edmund Eric Gah",
    url: "https://github.com/Eddiegah",
    sameAs: ["https://github.com/Eddiegah"],
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-stone-50">
        <script
          type="application/ld+json"
          // eslint-disable-next-line react/no-danger
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        {children}
      </body>
    </html>
  );
}
