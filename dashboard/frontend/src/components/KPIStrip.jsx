import { useEffect, useState } from "react";
import { fetchSummary } from "../api/client";

export default function KPIStrip({ selectedBank }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchSummary(selectedBank).then(setData);
  }, [selectedBank]);

  if (!data) return <div className="kpi-strip loading">Loading KPIs...</div>;

  const kpis = [
    {
      label: "Total Reviews",
      value: data.total_reviews?.toLocaleString() || "0",
      icon: "📝",
    },
    { label: "Avg Rating", value: `${data.avg_rating || "—"} ★`, icon: "⭐" },
    { label: "Avg Sentiment", value: data.avg_sentiment ?? "—", icon: "📈" },
    {
      label: "% Positive",
      value: `${data.pct_positive || 0}%`,
      icon: "😊",
      className: "positive",
    },
    {
      label: "% Negative",
      value: `${data.pct_negative || 0}%`,
      icon: "😞",
      className: "negative",
    },
  ];

  return (
    <div className="kpi-strip">
      {kpis.map((kpi) => (
        <div key={kpi.label} className={`kpi-card ${kpi.className || ""}`}>
          <span className="kpi-icon">{kpi.icon}</span>
          <div className="kpi-value">{kpi.value}</div>
          <div className="kpi-label">{kpi.label}</div>
        </div>
      ))}
    </div>
  );
}
