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
import { fetchThemes, fetchBanks } from "../api/client";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

/**
 * Pain Points & Drivers per Bank.
 *
 * Matches the `plot_theme_sentiment_bars` visualization from insight.ipynb:
 * one horizontal bar chart per bank showing mean sentiment per theme,
 * green for drivers (positive) and red for pain points (negative).
 *
 * When a single bank is selected, only that bank is shown.
 * When "All" is selected, one chart per bank is rendered side-by-side.
 */
export default function PainPointsDrivers({ selectedBank }) {
  const [banks, setBanks] = useState([]);
  const [dataByBank, setDataByBank] = useState({});

  const loadData = useCallback(() => {
    // Determine which banks to load
    const loadBanks =
      selectedBank === "All" ? fetchBanks() : Promise.resolve([selectedBank]);

    loadBanks.then((bankList) => {
      setBanks(bankList);
      const promises = bankList.map((bank) =>
        fetchThemes(bank).then((themes) => ({ bank, themes: themes || [] })),
      );
      Promise.all(promises).then((results) => {
        const map = {};
        for (const { bank, themes } of results) {
          // Sort by avg_sentiment ascending (pain points first, drivers last)
          const sorted = [...themes].sort(
            (a, b) => (a.avg_sentiment || 0) - (b.avg_sentiment || 0),
          );
          map[bank] = sorted;
        }
        setDataByBank(map);
      });
    });
  }, [selectedBank]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (banks.length === 0)
    return <p className="loading-text">Loading Pain Points &amp; Drivers…</p>;

  return (
    <section className="pain-drivers-section">
      <h3 className="section-title">
        Pain Points ← → Drivers{" "}
        <span className="section-subtitle">
          (Mean Sentiment by Theme per Bank)
        </span>
      </h3>
      <div
        className="pain-drivers-grid"
        style={{
          gridTemplateColumns: `repeat(${Math.min(banks.length, 3)}, 1fr)`,
        }}
      >
        {banks.map((bank) => {
          const themes = dataByBank[bank];
          if (!themes) return null;

          const labels = themes.map((t) => t.theme || "Unknown");
          const sentiments = themes.map((t) => t.avg_sentiment || 0);
          const colors = sentiments.map((v) =>
            v >= 0 ? "rgba(46,204,113,0.85)" : "rgba(231,76,60,0.85)",
          );

          const chartData = {
            labels,
            datasets: [
              {
                label: "Mean Sentiment",
                data: sentiments,
                backgroundColor: colors,
                borderRadius: 3,
                barThickness: 18,
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
                  label: (ctx) => `Mean Sentiment: ${ctx.raw.toFixed(3)}`,
                },
              },
            },
            scales: {
              x: {
                ticks: { color: "#aaa", font: { size: 10 } },
                grid: { color: "rgba(255,255,255,0.06)" },
                title: {
                  display: true,
                  text: "Mean Sentiment",
                  color: "#aaa",
                  font: { size: 11 },
                },
              },
              y: {
                ticks: { color: "#ddd", font: { size: 11 } },
                grid: { display: false },
              },
            },
          };

          // Dynamic height based on number of theme bars
          const chartHeight = Math.max(180, themes.length * 38);

          return (
            <div key={bank} className="glass-card pain-driver-card">
              <h4 className="pd-bank-title">{bank}</h4>
              <div style={{ height: chartHeight }}>
                <Bar data={chartData} options={options} />
              </div>
              {/* Zero-line indicator */}
              <p className="pd-legend">
                <span className="pd-dot pd-red" /> Pain Point&nbsp;&nbsp;
                <span className="pd-dot pd-green" /> Driver
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
