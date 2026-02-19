import { useEffect, useState } from "react";
import { fetchThemes } from "../api/client";
import ThemeCard from "./ThemeCard";

export default function ReviewsExplorer({ selectedBank }) {
  const [themes, setThemes] = useState([]);

  useEffect(() => {
    fetchThemes(selectedBank).then(setThemes);
  }, [selectedBank]);

  return (
    <section className="reviews-explorer">
      <h2 className="section-title">📋 Reviews Explorer</h2>
      <p className="section-sub">
        Click a theme to explore positive & negative reviews, sorted by topic
        confidence.
      </p>
      {themes.length === 0 ? (
        <p className="loading-text">Loading themes...</p>
      ) : (
        themes.map((t) => (
          <ThemeCard key={t.theme} theme={t} selectedBank={selectedBank} />
        ))
      )}
    </section>
  );
}
