"""
Insert cleaned review data into PostgreSQL.

Usage:
    1. Install PostgreSQL and create database:
       CREATE DATABASE bank_reviews;

    2. Run schema first:
       psql -U postgres -d bank_reviews -f scripts/schema.sql

    3. Install psycopg2:
       pip install psycopg2-binary

    4. Run this script:
       python scripts/insert_reviews.py
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# ── Load environment variables ────────────────────────────────
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "bank_reviews"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

# Path to the cleaned CSV
CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "processed", "reviews_with_themes_lda.csv"
)


def main():
    # ── 1. Load CSV ───────────────────────────────────────────
    print(f"Loading CSV from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"  → {len(df):,} reviews loaded")
    print(f"  → Columns: {list(df.columns)}")

    # ── 2. Connect to PostgreSQL ──────────────────────────────
    print(f"\nConnecting to PostgreSQL ({DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}) ...")
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()
    print("  → Connected!")

    try:
        # ── 3. Get bank_id mapping ───────────────────────────
        cur.execute("SELECT bank_id, bank_code FROM banks")
        bank_map = {code: bid for bid, code in cur.fetchall()}
        print(f"\nBank mapping: {bank_map}")

        if not bank_map:
            print("ERROR: No banks found! Did you run schema.sql first?")
            print("  → psql -U postgres -d bank_reviews -f scripts/schema.sql")
            sys.exit(1)

        # ── 4. Prepare rows for bulk insert ──────────────────
        print(f"\nPreparing {len(df):,} rows for insertion ...")

        rows = []
        skipped = 0
        for _, r in df.iterrows():
            bank_id = bank_map.get(r['bank_code'])
            if bank_id is None:
                skipped += 1
                continue

            rows.append((
                r['review_id'],
                bank_id,
                r['review_text'],
                int(r['rating']),
                r['review_date'],
                int(r['review_year']),
                int(r['review_month']),
                r['user_name'],
                int(r['thumbs_up']),
                int(r['text_length']),
                r['source'],
                float(r['sentiment_score']),
                r['sentiment_label'],
                r['clean_text'],
                int(r['topic_id']),
                float(r['topic_confidence']),
                r['identified_topic'],
                r['theme'],
            ))

        if skipped:
            print(f"  ⚠ Skipped {skipped} rows (unknown bank_code)")

        # ── 5. Bulk insert using execute_values (fast) ───────
        insert_sql = """
            INSERT INTO reviews (
                review_id, bank_id, review_text, rating,
                review_date, review_year, review_month,
                user_name, thumbs_up, text_length, source,
                sentiment_score, sentiment_label, clean_text,
                topic_id, topic_confidence, identified_topic, theme
            ) VALUES %s
            ON CONFLICT (review_id) DO NOTHING
        """

        print(f"  Inserting {len(rows):,} rows ...")
        execute_values(cur, insert_sql, rows, page_size=500)
        conn.commit()
        print(f"  → Insert complete!")

        # ── 6. Verify ────────────────────────────────────────
        print("\n── Verification ──")

        cur.execute("""
            SELECT b.bank_name, COUNT(*) AS review_count
            FROM reviews r JOIN banks b ON r.bank_id = b.bank_id
            GROUP BY b.bank_name ORDER BY review_count DESC
        """)
        print("\nReview counts per bank:")
        for bank_name, count in cur.fetchall():
            print(f"  {bank_name}: {count:,}")

        cur.execute("""
            SELECT b.bank_name,
                   ROUND(AVG(r.rating), 2) AS avg_rating,
                   ROUND(AVG(r.sentiment_score)::numeric, 3) AS avg_sentiment
            FROM reviews r JOIN banks b ON r.bank_id = b.bank_id
            GROUP BY b.bank_name ORDER BY avg_rating DESC
        """)
        print("\nAverage rating & sentiment per bank:")
        for bank_name, avg_rating, avg_sentiment in cur.fetchall():
            print(f"  {bank_name}: rating={avg_rating}, sentiment={avg_sentiment}")

        cur.execute("SELECT COUNT(*) FROM reviews")
        total = cur.fetchone()[0]
        print(f"\nTotal reviews in database: {total:,}")
        print("\n✓ Done! Database is ready.")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ ERROR: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
