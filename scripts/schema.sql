-- ============================================================
-- Bank Reviews Database Schema
-- PostgreSQL schema for storing cleaned & processed review data
-- ============================================================

-- Run this file AFTER creating the database:
--   CREATE DATABASE bank_reviews;
--   \c bank_reviews
--   \i scripts/schema.sql

-- ── Banks table ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS banks (
    bank_id   SERIAL       PRIMARY KEY,
    bank_code VARCHAR(20)  NOT NULL UNIQUE,
    bank_name VARCHAR(100) NOT NULL,
    app_name  VARCHAR(100)
);

-- Seed bank data
INSERT INTO banks (bank_code, bank_name, app_name) VALUES
    ('Abyssinia', 'Abyssinia Bank',                'Abyssinia Mobile'),
    ('CBE',       'Commercial Bank of Ethiopia',   'CBE Birr'),
    ('Dashen',    'Dashen Bank',                   'Dashen Amole')
ON CONFLICT (bank_code) DO NOTHING;


-- ── Reviews table ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    review_id        VARCHAR(50)   PRIMARY KEY,
    bank_id          INTEGER       NOT NULL REFERENCES banks(bank_id),
    review_text      TEXT          NOT NULL,
    rating           SMALLINT      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_date      DATE,
    review_year      SMALLINT,
    review_month     SMALLINT,
    user_name        VARCHAR(200),
    thumbs_up        INTEGER       DEFAULT 0,
    text_length      INTEGER,
    source           VARCHAR(50)   DEFAULT 'Google Play',
    sentiment_score  REAL,
    sentiment_label  VARCHAR(20),
    clean_text       TEXT,
    topic_id         SMALLINT,
    topic_confidence REAL,
    identified_topic VARCHAR(200),
    theme            VARCHAR(200),
    created_at       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);

-- ── Indexes for common query patterns ────────────────────────
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id       ON reviews (bank_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating        ON reviews (rating);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment     ON reviews (sentiment_label);
CREATE INDEX IF NOT EXISTS idx_reviews_theme         ON reviews (theme);
CREATE INDEX IF NOT EXISTS idx_reviews_review_date   ON reviews (review_date);


-- ── Verification queries (run after inserting data) ──────────
-- SELECT b.bank_name, COUNT(*) AS review_count
-- FROM reviews r JOIN banks b ON r.bank_id = b.bank_id
-- GROUP BY b.bank_name ORDER BY review_count DESC;

-- SELECT b.bank_name, ROUND(AVG(r.rating), 2) AS avg_rating,
--        ROUND(AVG(r.sentiment_score)::numeric, 3) AS avg_sentiment
-- FROM reviews r JOIN banks b ON r.bank_id = b.bank_id
-- GROUP BY b.bank_name ORDER BY avg_rating DESC;
