import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import KPIStrip from "./components/KPIStrip";
import ThemeDistChart from "./components/ThemeDistChart";
import SentimentDonut from "./components/SentimentDonut";
import PainPointsDrivers from "./components/PainPointsDrivers";
import ReviewsExplorer from "./components/ReviewsExplorer";
import { fetchBanks } from "./api/client";
import "./App.css";

export default function App() {
  const [banks, setBanks] = useState([]);
  const [selectedBank, setSelectedBank] = useState("All");

  useEffect(() => {
    fetchBanks().then(setBanks);
  }, []);

  return (
    <div className="app-layout">
      <Sidebar
        banks={banks}
        selectedBank={selectedBank}
        onSelectBank={setSelectedBank}
      />
      <main className="main-content">
        <header className="page-header">
          <h2>
            {selectedBank === "All" ? "All Banks" : selectedBank}
            <span className="header-sub"> — Customer Experience Dashboard</span>
          </h2>
        </header>

        <KPIStrip selectedBank={selectedBank} />

        <section className="charts-row">
          <div className="chart-col theme-chart-col">
            <ThemeDistChart selectedBank={selectedBank} />
          </div>
          <div className="chart-col sentiment-chart-col">
            <SentimentDonut selectedBank={selectedBank} />
          </div>
        </section>

        <PainPointsDrivers selectedBank={selectedBank} />

        <ReviewsExplorer selectedBank={selectedBank} />
      </main>
    </div>
  );
}
