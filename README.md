# Customer Experience Analytics for Fintech Apps

This project analyzes customer reviews for Ethiopian banking apps (CBE, Abyssinia, Dashen) from the Google Play Store. It includes a pipeline for scraping, preprocessing, and analyzing user feedback to derive insights into customer satisfaction.

## Project Structure

```
Customer-Experience-Analytics-for-Fintech-Apps/
├── data/
│   ├── raw/                # Raw scraped data (CSV)
│   └── processed/          # Cleaned and preprocessed data (CSV)
├── notebooks/
│   └── scrape_data.ipynb   # Jupyter notebook for running the pipeline interactively
├── src/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration settings (App IDs, paths, etc.)
│   ├── preprocessing.py    # Data cleaning and preprocessing logic
│   └── scraper.py          # Google Play Store scraping logic
├── .env                    # Environment variables (API keys, config overrides)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## Features

*   **Scraper:** Fetches the latest reviews from the Google Play Store for configured apps.
*   **Preprocessing:**
    * Removes rows with missing critical data. and drops columns with excessive missing values.
    *   Removes duplicate reviews.
    *   Filters out reviews containing Amharic text (for English NLP analysis).
    *   Normalizes dates and cleans text.
    *   Validates ratings (1-5 stars).
*   **Analysis:** (In progress) Sentiment analysis and topic modeling.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MYGBM/Customer-Experience-Analytics-for-Fintech-Apps.git
    cd Customer-Experience-Analytics-for-Fintech-Apps
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file in the root directory (optional, defaults are in `src/config.py`):
    ```env
    REVIEWS_PER_BANK=500
    MAX_RETRIES=3
    ```

## Usage

### Running via Notebook
Open `notebooks/scrape_data.ipynb` in Jupyter or VS Code and run the cells sequentially to:
1.  Scrape new data.
2.  Preprocess the data.
3.  Visualize basic statistics.

### Running via Scripts
You can also run the modules directly from the project root:

**Scrape Data:**
```bash
python -m src.scraper
```

**Preprocess Data:**
```bash
python -m src.preprocessing
```

## Data Pipeline
1.  **Raw Data:** Saved to `data/raw/reviews_raw.csv`
2.  **Processed Data:** Saved to `data/processed/reviews_processed.csv`
