"""
FastAPI backend for the Customer Experience Analytics Dashboard.
Serves review data from PostgreSQL to the React frontend.
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database import fetch_all, fetch_one
from typing import Optional

app = FastAPI(
    title="Bank Reviews Analytics API",
    description="API for the Customer Experience Analytics Dashboard",
    version="1.0.0",
)

# Allow React dev server (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _bank_filter(bank: Optional[str]) -> tuple[str, tuple]:
    """Return SQL WHERE clause and params for optional bank filter."""
    if bank and bank.lower() != "all":
        return "WHERE b.bank_name = %s", (bank,)
    return "", ()


# ── Banks ────────────────────────────────────────────────────────
@app.get("/api/banks")
def get_banks():
    """Return list of bank names."""
    rows = fetch_all("SELECT bank_name FROM banks ORDER BY bank_name")
    return [r["bank_name"] for r in rows]


# ── Summary KPIs ─────────────────────────────────────────────────
@app.get("/api/summary")
def get_summary(bank: Optional[str] = Query(None)):
    """
    Return KPI summary: total reviews, avg rating, avg sentiment,
    % positive, % negative.
    """
    where, params = _bank_filter(bank)
    query = f"""
        SELECT
            COUNT(*)                               AS total_reviews,
            ROUND(AVG(r.rating)::numeric, 2)       AS avg_rating,
            ROUND(AVG(r.sentiment_score)::numeric, 3) AS avg_sentiment,
            ROUND(100.0 * SUM(CASE WHEN r.sentiment_label = 'positive' THEN 1 ELSE 0 END)
                  / NULLIF(COUNT(*), 0), 1)        AS pct_positive,
            ROUND(100.0 * SUM(CASE WHEN r.sentiment_label = 'negative' THEN 1 ELSE 0 END)
                  / NULLIF(COUNT(*), 0), 1)        AS pct_negative
        FROM reviews r
        JOIN banks b ON r.bank_id = b.bank_id
        {where}
    """
    return fetch_one(query, params)


# ── Theme Distribution ───────────────────────────────────────────
@app.get("/api/themes")
def get_themes(bank: Optional[str] = Query(None)):
    """
    Return theme name, review count, and avg sentiment per theme.
    Sorted by count descending.
    """
    where, params = _bank_filter(bank)
    query = f"""
        SELECT
            r.theme,
            COUNT(*)                               AS review_count,
            ROUND(AVG(r.sentiment_score)::numeric, 3) AS avg_sentiment
        FROM reviews r
        JOIN banks b ON r.bank_id = b.bank_id
        {where}
        GROUP BY r.theme
        ORDER BY review_count DESC
    """
    return fetch_all(query, params)


# ── Sentiment Distribution ───────────────────────────────────────
@app.get("/api/sentiment")
def get_sentiment(bank: Optional[str] = Query(None)):
    """
    Return counts of positive, neutral, negative reviews.
    Optionally per bank.
    """
    where, params = _bank_filter(bank)
    query = f"""
        SELECT
            r.sentiment_label,
            COUNT(*) AS count
        FROM reviews r
        JOIN banks b ON r.bank_id = b.bank_id
        {where}
        GROUP BY r.sentiment_label
        ORDER BY r.sentiment_label
    """
    rows = fetch_all(query, params)
    # Return as dict: {positive: N, negative: N, neutral: N}
    result = {"positive": 0, "negative": 0, "neutral": 0}
    for row in rows:
        label = row["sentiment_label"]
        if label in result:
            result[label] = row["count"]
    return result


# ── Reviews (paginated) ──────────────────────────────────────────
@app.get("/api/reviews")
def get_reviews(
    bank: Optional[str] = Query(None),
    theme: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Return paginated reviews sorted by topic_confidence DESC.
    Filterable by bank, theme, and sentiment label.
    """
    conditions = []
    params = []

    if bank and bank.lower() != "all":
        conditions.append("b.bank_name = %s")
        params.append(bank)
    if theme:
        conditions.append("r.theme = %s")
        params.append(theme)
    if sentiment:
        conditions.append("r.sentiment_label = %s")
        params.append(sentiment)

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    offset = (page - 1) * limit
    params.extend([limit, offset])

    query = f"""
        SELECT
            r.review_id,
            r.review_text,
            r.rating,
            r.review_date,
            b.bank_name,
            r.sentiment_score,
            r.sentiment_label,
            r.topic_confidence,
            r.theme
        FROM reviews r
        JOIN banks b ON r.bank_id = b.bank_id
        {where}
        ORDER BY r.topic_confidence DESC
        LIMIT %s OFFSET %s
    """
    reviews = fetch_all(query, tuple(params))

    # Also get total count for pagination
    count_query = f"""
        SELECT COUNT(*) AS total
        FROM reviews r
        JOIN banks b ON r.bank_id = b.bank_id
        {where}
    """
    count_params = tuple(params[:-2])  # exclude limit and offset
    total = fetch_one(count_query, count_params)

    return {
        "reviews": reviews,
        "total": total["total"] if total else 0,
        "page": page,
        "limit": limit,
    }


# ── Sentiment by Theme (for charts) ─────────────────────────────
@app.get("/api/theme-sentiment")
def get_theme_sentiment(bank: Optional[str] = Query(None)):
    """
    Return per-theme sentiment breakdown (for stacked/grouped charts).
    """
    where, params = _bank_filter(bank)
    query = f"""
        SELECT
            r.theme,
            r.sentiment_label,
            COUNT(*) AS count,
            ROUND(AVG(r.sentiment_score)::numeric, 3) AS avg_sentiment,
            ROUND(MIN(r.sentiment_score)::numeric, 3) AS min_sentiment,
            ROUND(MAX(r.sentiment_score)::numeric, 3) AS max_sentiment
        FROM reviews r
        JOIN banks b ON r.bank_id = b.bank_id
        {where}
        GROUP BY r.theme, r.sentiment_label
        ORDER BY r.theme, r.sentiment_label
    """
    return fetch_all(query, params)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
