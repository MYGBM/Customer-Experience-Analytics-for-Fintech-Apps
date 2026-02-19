import { useState, useEffect } from "react";

const BANK_COLORS = {
  "Abyssinia Bank": "#e74c3c",
  "Commercial Bank of Ethiopia": "#3498db",
  "Dashen Bank": "#2ecc71",
};

export default function Sidebar({ banks, selectedBank, onSelectBank }) {
  const [bankList, setBankList] = useState([]);

  useEffect(() => {
    setBankList(banks);
  }, [banks]);

  return (
    <aside className="sidebar">
      <h1 className="sidebar-title">📊 CX Analytics</h1>
      <nav className="bank-nav">
        <button
          className={`bank-btn ${selectedBank === "All" ? "active" : ""}`}
          onClick={() => onSelectBank("All")}
        >
          All Banks
        </button>
        {bankList.map((b) => (
          <button
            key={b}
            className={`bank-btn ${selectedBank === b ? "active" : ""}`}
            style={
              selectedBank === b
                ? { borderColor: BANK_COLORS[b] || "#888" }
                : {}
            }
            onClick={() => onSelectBank(b)}
          >
            {b}
          </button>
        ))}
      </nav>
    </aside>
  );
}
