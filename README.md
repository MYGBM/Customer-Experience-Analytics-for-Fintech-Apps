# Customer Experience Analytics for Fintech Apps

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg?style=flat&logo=fastapi&logoColor=white) ![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=flat&logo=react&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF.svg?logo=vite&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0+-4169E1.svg?logo=postgresql&logoColor=white) ![Gensim](https://img.shields.io/badge/Gensim-4.0+-brightgreen.svg) ![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Hugging%20Face-yellow.svg) ![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**End-to-End Sentiment & Thematic Analysis for Ethiopian Banking Apps**

This project provides a comprehensive analytics platform to understand user feedback for **Commercial Bank of Ethiopia (CBE)**, **Abyssinia Bank (Apollo)**, and **Dashen Bank (Amole)**. It moves beyond simple star ratings to extract detailed insights using advanced NLP techniques (Twitter-RoBERTa) and unsupervised learning (LDA).

---

## 🚀 Key Features

- **Automated Scraping**: Robust scraping pipeline for Google Play Store reviews with retry mechanisms.
- **Advanced Sentiment Analysis**: Comparison of VADER (Rule-based) vs. Twitter-RoBERTa (Deep Learning) models.
- **Thematic Discovery**: Latent Dirichlet Allocation (LDA) to uncover hidden topics like "Login Failures" and "Update Instability".
- **Interactive Dashboard**: A full-stack web application (React + FastAPI) to visualize insights, filter by bank, and explore key drivers of satisfaction.

---

## 📂 Repository Structure

```
Customer-Experience-Analytics-for-Fintech-Apps/
├── dashboard/                  # Interactive Dashboard
│   ├── backend/                # FastAPI Backend
│   │   ├── main.py             # API Entry Point
│   │   └── database.py         # Database Connection
│   └── frontend/               # React Frontend
│       ├── src/
│       │   ├── components/     # Reusable Charts & UI Components
│       │   ├── pages/          # Dashboard Pages
│       │   └── App.jsx         # Main App Component
│       └── package.json        # Frontend Dependencies
├── notebooks/                  # Analysis Notebooks (Run in Order)
│   ├── 1_scrape_data.ipynb     # Data Collection
│   ├── 2_vader_sentiment.ipynb # Baseline Sentiment Analysis
│   ├── 3_twitter_roberta.ipynb # Advanced Sentiment Analysis
│   ├── 4_theme_analysis_lda.ipynb # Topic Modeling
│   └── 5_insight.ipynb         # Final Insights & Visualization Generation
├── src/                        # Core Python Modules
│   ├── scraper.py              # PlayStoreScraper Class
│   ├── sentiment_twitter.py    # RoBERTa Pipeline
│   ├── theme_analysis_lda.py   # LDA Implementation
│   ├── insight_visualizations.py # Visualization Logic
│   └── config.py               # Configuration Settings
├── reports/                    # Generated Reports
│   └── report.md               # Comprehensive Final Report
├── requirements.txt            # Python Dependencies
└── README.md                   # Project Documentation
```

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js & npm (for Dashboard)
- PostgreSQL (optional, for production backend)

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/cx-analytics.git
cd cx-analytics
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

_Note: This will install `torch`, `transformers`, `google-play-scraper`, `pandas`, `fastapi`, and other required libraries._

### 3. Set Up Dashboard (Frontend)

```bash
cd dashboard/frontend
npm install
```

---

## 📊 Usage Guide

### A. Run the Analysis Pipeline

Execute the notebooks in the `notebooks/` directory sequentially to scrape data, run models, and generate insights.

1.  **Scrape Data**: `notebooks/1_scrape_data.ipynb`
2.  **Run Sentiment Models**: `notebooks/3_twitter_roberta.ipynb`
3.  **Extract Themes**: `notebooks/4_theme_analysis_lda.ipynb`
4.  **Generate Insights**: `notebooks/5_insight.ipynb`

### B. Launch the Dashboard

To explore the results interactively:

**1. Start the Backend API:**

```bash
# From the root directory
cd dashboard/backend
uvicorn main:app --reload
```

**2. Start the Frontend:**

```bash
# From dashboard/frontend
npm run dev
```

Open your browser to `http://localhost:5173` to view the dashboard.

---

## 📈 Methodology Highlights

### Sentiment Analysis

We transitioned from **VADER** to **Twitter-RoBERTa**, achieving a **72.1% accuracy** and significantly improving the detection of negative reviews (Recall: 71.5%). This ensures critical user complaints—often phrased neutrally like "I can't login"—are correctly flagged.

### Topic Modeling (LDA)

We trained separate LDA models for each bank to capture their unique context.

- **CBE**: 5 Topics (Dominant: "App Stability")
- **Abyssinia**: 8 Topics (Dominant: "Transaction & OTP Issues")
- **Dashen**: 3 Topics (Dominant: "Super App Features")

---

## 📝 contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

**License:** MIT
