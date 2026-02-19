import { useState, useEffect, useCallback } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { fetchThemes } from "../api/client";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function ThemeDistChart({ selectedBank }) {
  const [themes, setThemes] = useState([]);

  const loadData = useCallback(() => {
    fetchThemes(selectedBank).then((data) => setThemes(data || []));
  }, [selectedBank]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (themes.length === 0) return <p className="loading-text">Loading…</p>;

  const labels = themes.map((t) => t.theme || "Unknown");
  const counts = themes.map((t) => t.review_count);
  const colors = themes.map((t) =>
    (t.avg_sentiment || 0) >= 0 ? "#2ecc71" : "#e74c3c",
  );

  const chartData = {
    labels,
    datasets: [
      {
        label: "Reviews",
        data: counts,
        backgroundColor: colors,
        borderRadius: 4,
      },
    ],
  };

  const options = {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          afterLabel: (ctx) => {
            const t = themes[ctx.dataIndex];
            return `Avg sentiment: ${t.avg_sentiment}`;
          },
        },
      },
    },
    scales: {
      x: { ticks: { color: "#aaa" }, grid: { color: "rgba(255,255,255,.06)" } },
      y: {
        ticks: { color: "#ddd", font: { size: 11 } },
        grid: { display: false },
      },
    },
  };

  return (
    <div className="glass-card chart-card">
      <h3 className="card-title">Theme Distribution</h3>
      <div className="bar-wrapper">
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
}
