import { useState, useEffect, useCallback } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Doughnut } from "react-chartjs-2";
import { fetchSentiment } from "../api/client";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function SentimentDonut({ selectedBank }) {
  const [data, setData] = useState(null);

  const loadData = useCallback(() => {
    fetchSentiment(selectedBank).then(setData);
  }, [selectedBank]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (!data) return <p className="loading-text">Loading…</p>;

  const total =
    (data.positive || 0) + (data.neutral || 0) + (data.negative || 0);

  const chartData = {
    labels: ["Positive", "Neutral", "Negative"],
    datasets: [
      {
        data: [data.positive || 0, data.neutral || 0, data.negative || 0],
        backgroundColor: ["#2ecc71", "#f39c12", "#e74c3c"],
        borderWidth: 0,
      },
    ],
  };

  const options = {
    cutout: "65%",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom",
        labels: { color: "#ccc", font: { size: 12 } },
      },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const val = ctx.raw;
            const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
            return `${ctx.label}: ${val} (${pct}%)`;
          },
        },
      },
    },
  };

  return (
    <div className="glass-card chart-card">
      <h3 className="card-title">Sentiment Breakdown</h3>
      <div className="donut-wrapper">
        <Doughnut data={chartData} options={options} />
        <div className="donut-center">
          <span className="donut-total">{total}</span>
          <span className="donut-label">reviews</span>
        </div>
      </div>
    </div>
  );
}
