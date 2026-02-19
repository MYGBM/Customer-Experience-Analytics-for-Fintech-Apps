import { useState, useEffect, useRef, useCallback } from "react";
import { fetchReviews } from "../api/client";
import ReviewRow from "./ReviewRow";

export default function ThemeCard({ theme, selectedBank }) {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState("positive");
  const [reviews, setReviews] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const loadingRef = useRef(false);

  const loadReviews = useCallback(() => {
    if (!open) return;
    loadingRef.current = true;
    setLoading(true);
    fetchReviews(selectedBank, theme.theme, tab, page, 10).then((res) => {
      if (!loadingRef.current) return;
      setReviews(res.reviews || []);
      setTotal(res.total || 0);
      setLoading(false);
    });
  }, [open, tab, page, selectedBank, theme.theme]);

  useEffect(() => {
    // eslint-disable-next-line
    loadReviews();
    return () => {
      loadingRef.current = false;
    };
  }, [loadReviews]);

  const sentimentBadge =
    theme.avg_sentiment >= 0 ? "badge-positive" : "badge-negative";
  const totalPages = Math.ceil(total / 10);

  return (
    <div className="theme-card">
      <div className="theme-card-header" onClick={() => setOpen(!open)}>
        <div className="theme-info">
          <h3 className="theme-name">{theme.theme || "Unknown"}</h3>
          <span className="theme-count">{theme.review_count} reviews</span>
          <span className={`theme-badge ${sentimentBadge}`}>
            {theme.avg_sentiment >= 0 ? "+" : ""}
            {theme.avg_sentiment}
          </span>
        </div>
        <span className={`chevron ${open ? "open" : ""}`}>▶</span>
      </div>

      {open && (
        <div className="theme-card-body">
          <div className="tab-bar">
            <button
              className={`tab-btn ${tab === "positive" ? "active tab-positive" : ""}`}
              onClick={() => {
                setTab("positive");
                setPage(1);
              }}
            >
              😊 Positive
            </button>
            <button
              className={`tab-btn ${tab === "negative" ? "active tab-negative" : ""}`}
              onClick={() => {
                setTab("negative");
                setPage(1);
              }}
            >
              😞 Negative
            </button>
          </div>

          {loading ? (
            <p className="loading-text">Loading reviews...</p>
          ) : reviews.length === 0 ? (
            <p className="empty-text">No {tab} reviews for this theme.</p>
          ) : (
            <>
              <div className="reviews-list">
                {reviews.map((r) => (
                  <ReviewRow key={r.review_id} review={r} />
                ))}
              </div>
              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    disabled={page <= 1}
                    onClick={() => setPage(page - 1)}
                  >
                    ← Prev
                  </button>
                  <span>
                    Page {page} of {totalPages}
                  </span>
                  <button
                    disabled={page >= totalPages}
                    onClick={() => setPage(page + 1)}
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
