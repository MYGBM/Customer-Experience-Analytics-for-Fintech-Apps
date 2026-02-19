"""
Configuration file for Bank Reviews Analysis Project
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Play Store App IDs
APP_IDS = {
# env
    'CBE': os.getenv('CBE_APP_ID', 'com.combanketh.mobilebanking'),
    'Abyssinia': os.getenv('Abyssinia_APP_ID', 'com.boa.boaMobileBanking'),
    'Dashen': os.getenv('DASHEN_APP_ID', 'com.dashen.dashensuperapp')

}

# Bank Names Mapping
BANK_NAMES = {
    'CBE': 'Commercial Bank of Ethiopia',
    'Abyssinia': 'Abyssinia Bank',
    'Dashen': 'Dashen Bank'
}

# Scraping Configuration
SCRAPING_CONFIG = {
    'reviews_per_bank': {
        'CBE': 8300,
        'Abyssinia': 1200,
        'Dashen': 770
    },
    'max_retries': int(os.getenv('MAX_RETRIES', 3)),
    'lang': 'en',
    'country': 'et'  # Ethiopia
}

# File Paths
DATA_PATHS = {
    'raw': '../data/raw',
    'processed': '../data/processed',
    'raw_reviews': '../data/raw/reviews_raw.csv',
    'processed_reviews': '../data/processed/reviews_processed.csv',
    
    # it looks as if theme_prepared is not really being used for sentiment analysis but just keep in case because vader uses the raw processed data and bert does it's own preprocessing maybe it might be used for topic modelling but highly unlikely since spacy will most liekly be used there
    'theme_prepared': '../data/processed/reviews_for_theme.csv',
    #Have updated the name of the file to reflect that it is vader sentiment analysis
    'sentiment_results_vader': '../data/processed/reviews_with_vader_sentiment.csv',
    'sentiment_results_twitter': '../data/processed/reviews_with_twitter_sentiment.csv',
    'sentiment_results_bert': '../data/processed/reviews_with_sentiment_bert.csv',
    'theme_results': '../data/processed/reviews_with_themes.csv',
    'theme_results_lda': '../data/processed/reviews_with_themes_lda.csv',
    'final_results': '../data/processed/reviews_final.csv',
    "theme_analysis": "../data/processed/theme_analysis.csv"
}

# Visualization Style
PLOT_STYLE = 'seaborn-v0_8'









