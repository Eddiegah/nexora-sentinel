import { useState, useEffect } from "react";

const styles = {
  app: {
    fontFamily: "'Segoe UI', sans-serif",
    backgroundColor: "#0f172a",
    minHeight: "100vh",
    color: "#f1f5f9",
  },
  header: {
    backgroundColor: "#1e293b",
    padding: "20px 40px",
    borderBottom: "1px solid #334155",
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  headerTitle: {
    fontSize: "24px",
    fontWeight: "700",
    color: "#38bdf8",
    margin: "0",
  },
  headerSub: {
    fontSize: "13px",
    color: "#94a3b8",
    margin: "0",
  },
  badge: {
    backgroundColor: "#22c55e",
    color: "white",
    fontSize: "11px",
    padding: "3px 8px",
    borderRadius: "999px",
    fontWeight: "600",
  },
  main: {
    padding: "32px 40px",
    maxWidth: "1100px",
    margin: "0 auto",
  },
  card: {
    backgroundColor: "#1e293b",
    borderRadius: "12px",
    padding: "24px",
    marginBottom: "24px",
    border: "1px solid #334155",
  },
  cardTitle: {
    fontSize: "16px",
    fontWeight: "600",
    color: "#94a3b8",
    marginBottom: "16px",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  select: {
    backgroundColor: "#0f172a",
    color: "#f1f5f9",
    border: "1px solid #475569",
    borderRadius: "8px",
    padding: "10px 16px",
    fontSize: "15px",
    width: "100%",
    marginBottom: "12px",
    cursor: "pointer",
  },
  button: {
    backgroundColor: "#38bdf8",
    color: "#0f172a",
    border: "none",
    borderRadius: "8px",
    padding: "12px 28px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
    width: "100%",
    marginBottom: "8px",
  },
  buttonSecondary: {
    backgroundColor: "#334155",
    color: "#f1f5f9",
    border: "none",
    borderRadius: "8px",
    padding: "12px 28px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
    width: "100%",
    marginBottom: "8px",
  },
  riskCard: (color) => ({
    backgroundColor: "#0f172a",
    border: `2px solid ${color}`,
    borderRadius: "12px",
    padding: "24px",
    textAlign: "center",
    marginTop: "16px",
  }),
  riskLevel: (color) => ({
    fontSize: "48px",
    fontWeight: "800",
    color: color,
    margin: "0",
  }),
  reportBox: {
    backgroundColor: "#0f172a",
    border: "1px solid #334155",
    borderRadius: "12px",
    padding: "20px",
    marginTop: "16px",
    lineHeight: "1.7",
    fontSize: "14px",
    color: "#cbd5e1",
    whiteSpace: "pre-wrap",
  },
  reportTitle: {
    fontSize: "13px",
    fontWeight: "600",
    color: "#38bdf8",
    marginBottom: "12px",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    textAlign: "left",
    padding: "12px 16px",
    fontSize: "12px",
    color: "#64748b",
    borderBottom: "1px solid #334155",
    textTransform: "uppercase",
  },
  td: {
    padding: "12px 16px",
    borderBottom: "1px solid #1e293b",
    fontSize: "14px",
  },
  dot: (color) => ({
    display: "inline-block",
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    backgroundColor: color,
    marginRight: "8px",
  }),
  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr 1fr",
    gap: "16px",
    marginBottom: "24px",
  },
  statCard: {
    backgroundColor: "#1e293b",
    borderRadius: "12px",
    padding: "20px",
    border: "1px solid #334155",
    textAlign: "center",
  },
  statNumber: {
    fontSize: "36px",
    fontWeight: "800",
    color: "#38bdf8",
  },
  statLabel: {
    fontSize: "12px",
    color: "#64748b",
    marginTop: "4px",
  },
};

export default function App() {
  const [countries, setCountries] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState("Ghana");
  const [selectedYear, setSelectedYear] = useState(2024);
  const [prediction, setPrediction] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [allPredictions, setAllPredictions] = useState([]);
  const [loadingAll, setLoadingAll] = useState(false);

const API = "http://34.201.137.167:8000";

  useEffect(() => {
    fetch(`${API}/countries`)
      .then((res) => res.json())
      .then((data) => setCountries(data.countries))
      .catch(() => setCountries(["Ghana", "Nigeria", "Kenya"]));
  }, []);

  const getPrediction = async () => {
    setLoading(true);
    setReport(null);
    setPrediction(null);
    try {
      const res = await fetch(`${API}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          country: selectedCountry,
          year: selectedYear,
          urban_population_pct: 55,
          rural_population_pct: 45,
          urban_growth: 2.5,
          rural_growth: 1.5,
          water_access_pct: 60,
        }),
      });
      const data = await res.json();
      setPrediction(data);
    } catch (err) {
      setPrediction({ error: "Could not connect to API" });
    }
    setLoading(false);
  };

  const getReport = async () => {
    if (!prediction || prediction.error) return;
    setLoadingReport(true);
    try {
      const res = await fetch(`${API}/report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          country: prediction.country,
          year: prediction.year,
          risk_level: prediction.risk_level,
          confidence: prediction.confidence,
        }),
      });
      const data = await res.json();
      setReport(data);
    } catch (err) {
      setReport({ error: "Could not generate report" });
    }
    setLoadingReport(false);
  };

  const loadAllPredictions = async () => {
    setLoadingAll(true);
    const topCountries = [
      "Ghana", "Nigeria", "Kenya", "Ethiopia", "Tanzania",
      "Uganda", "Mozambique", "Mali", "Burkina Faso", "Niger",
      "Cameroon", "Senegal", "Zimbabwe", "Zambia", "Angola",
    ];
    const results = [];
    for (const country of topCountries) {
      try {
        const res = await fetch(`${API}/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            country,
            year: selectedYear,
            urban_population_pct: 55,
            rural_population_pct: 45,
            urban_growth: 2.5,
            rural_growth: 1.5,
            water_access_pct: 60,
          }),
        });
        const data = await res.json();
        if (!data.error) results.push(data);
      } catch {}
    }
    setAllPredictions(results);
    setLoadingAll(false);
  };

  const years = Array.from({ length: 10 }, (_, i) => 2020 + i);
  const highCount = allPredictions.filter(p => p.risk_level === "High").length;
  const medCount = allPredictions.filter(p => p.risk_level === "Medium").length;
  const lowCount = allPredictions.filter(p => p.risk_level === "Low").length;

  return (
    <div style={styles.app}>
      <div style={styles.header}>
        <div>
          <p style={styles.headerTitle}>🛡️ Nexora Sentinel</p>
          <p style={styles.headerSub}>
            AI-powered malaria outbreak prediction for Africa
          </p>
        </div>
        <span style={styles.badge}>LIVE</span>
      </div>

      <div style={styles.main}>
        <div style={styles.card}>
          <p style={styles.cardTitle}>🔍 Predict Outbreak Risk</p>
          <select
            style={styles.select}
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
          >
            {countries.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <select
            style={styles.select}
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
          >
            {years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <button style={styles.button} onClick={getPrediction}>
            {loading ? "Predicting..." : "Run Prediction"}
          </button>

          {prediction && !prediction.error && (
            <>
              <div style={styles.riskCard(prediction.color)}>
                <p style={{ color: "#94a3b8", margin: "0 0 8px 0", fontSize: "14px" }}>
                  {prediction.country} — {prediction.year}
                </p>
                <p style={styles.riskLevel(prediction.color)}>
                  {prediction.risk_level}
                </p>
                <p style={{ color: "#94a3b8", marginTop: "4px" }}>
                  Malaria Outbreak Risk
                </p>
                <p style={{ color: "#64748b", fontSize: "13px" }}>
                  Model confidence: {prediction.confidence}%
                </p>
              </div>

              <button
                style={{ ...styles.buttonSecondary, marginTop: "12px" }}
                onClick={getReport}
              >
                {loadingReport
                  ? "Generating AI Report..."
                  : "🧠 Generate AI Health Report"}
              </button>

              {report && !report.error && (
                <div style={styles.reportBox}>
                  <p style={styles.reportTitle}>
                    AI Health Intelligence Report — Powered by Claude
                  </p>
                  {report.report}
                </div>
              )}
            </>
          )}

          {prediction?.error && (
            <p style={{ color: "#ef4444", marginTop: "12px" }}>
              {prediction.error}
            </p>
          )}
        </div>

        <div style={styles.card}>
          <p style={styles.cardTitle}>🌍 Regional Risk Overview</p>
          <button style={styles.button} onClick={loadAllPredictions}>
            {loadingAll ? "Loading predictions..." : "Load Top 15 Countries"}
          </button>

          {allPredictions.length > 0 && (
            <>
              <div style={{ ...styles.grid, marginTop: "20px" }}>
                <div style={styles.statCard}>
                  <div style={{ ...styles.statNumber, color: "#ef4444" }}>
                    {highCount}
                  </div>
                  <div style={styles.statLabel}>HIGH RISK</div>
                </div>
                <div style={styles.statCard}>
                  <div style={{ ...styles.statNumber, color: "#f59e0b" }}>
                    {medCount}
                  </div>
                  <div style={styles.statLabel}>MEDIUM RISK</div>
                </div>
                <div style={styles.statCard}>
                  <div style={{ ...styles.statNumber, color: "#22c55e" }}>
                    {lowCount}
                  </div>
                  <div style={styles.statLabel}>LOW RISK</div>
                </div>
              </div>

              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Country</th>
                    <th style={styles.th}>Year</th>
                    <th style={styles.th}>Risk Level</th>
                    <th style={styles.th}>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {allPredictions.map((p) => (
                    <tr key={p.country}>
                      <td style={styles.td}>{p.country}</td>
                      <td style={styles.td}>{p.year}</td>
                      <td style={styles.td}>
                        <span style={styles.dot(p.color)} />
                        {p.risk_level}
                      </td>
                      <td style={styles.td}>{p.confidence}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      </div>
    </div>
  );
}