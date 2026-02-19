import { useState } from "react";

const SENTIMENT_COLORS = {
  positive: "#2ecc71",
  neutral: "#f39c12",
  negative: "#e74c3c",
};

export default function ReviewRow({ review }) {
  const [expanded, setExpanded] = useState(false);
  const r = review;
  const pillColor = SENTIMENT_COLORS[r.sentiment_label] || "#888";
  const confPct = Math.round((r.topic_confidence || 0) * 100);

  const stars = "★".repeat(r.rating || 0) + "☆".repeat(5 - (r.rating || 0));

  return (
    <div className="review-row" onClick={() => setExpanded(!expanded)}>
      <div className="review-top">
        <span className="review-stars">{stars}</span>
        <span className="sentiment-pill" style={{ backgroundColor: pillColor }}>
          {r.sentiment_label}
        </span>
        <span className="review-bank">{r.bank_name}</span>
      </div>

      <div className="confidence-bar-wrapper">
        <div className="confidence-label">Confidence {confPct}%</div>
        <div className="confidence-track">
          <div className="confidence-fill" style={{ width: `${confPct}%` }} />
        </div>
      </div>

      <p className={`review-text ${expanded ? "expanded" : ""}`}>
        {r.review_text}
      </p>
    </div>
  );
}
