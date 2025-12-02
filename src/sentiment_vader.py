"""
Sentiment Analysis Module
Task 2: Sentiment Analysis Pipeline

This script performs sentiment analysis on the preprocessed reviews.
- Tokenization, Lemmatization, Stopword Removal
- VADER Sentiment Analysis
"""

import sys
import os
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DATA_PATHS

class SentimentAnalysis:
    """Pipeline for sentiment analysis using NLTK VADER"""

    def __init__(self, input_path=None, prepared_path=None, output_path=None):
        """
        Initialize the sentiment analysis pipeline
        
        Args:
            input_path (str): Path to processed reviews CSV
            prepared_path (str): Path to save intermediate prepared data
            output_path (str): Path to save final sentiment results
        """
        self.input_path = input_path or DATA_PATHS['processed_reviews']
        self.prepared_path = prepared_path or DATA_PATHS['theme_prepared']
        self.output_path = output_path or DATA_PATHS['sentiment_results']
        self.df = None
        self.sia = None

    def load_data(self):
        """Load processed data"""
        print("Loading processed data...")
        try:
            self.df = pd.read_csv(self.input_path)
            print(f"Loaded {len(self.df)} reviews")
            return True
        except FileNotFoundError:
            print(f"ERROR: File not found: {self.input_path}")
            return False
        except Exception as e:
            print(f"ERROR: Failed to load data: {str(e)}")
            return False

    def preprocess_for_sentiment(self):
        """
        Perform text preprocessing for sentiment analysis context:
        1. Tokenization
        2. Stopword removal
        3. Lemmatization
        
        Saves the result to sentiment_prepared path.
        """
        print("\n[1/2] Preprocessing for sentiment analysis...")
        
        # Download necessary NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            print("Downloading NLTK resources...")
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('omw-1.4')

        lemmatizer = WordNetLemmatizer()
        stop_words = set(stopwords.words('english'))
        # Keep negation words
        for w in ['not', 'no', 'nor']:
            stop_words.discard(w)

        def process_text(text):
            if pd.isna(text):
                return ""
            
            # Tokenize
            # Ensure text is string and lowercased
            tokens = word_tokenize(str(text).lower())
            
            # Remove stopwords and non-alphabetic tokens, then lemmatize
            clean_tokens = [
                lemmatizer.lemmatize(word) 
                for word in tokens 
                if word.isalpha() and word not in stop_words
            ]
            
            return " ".join(clean_tokens)

        # Apply preprocessing
        print("Applying tokenization, stopword removal, and lemmatization...")
        self.df['theme_prepared_text'] = self.df['review_text'].apply(process_text)
        
        # Save intermediate data
        try:
            os.makedirs(os.path.dirname(self.prepared_path), exist_ok=True)
            self.df.to_csv(self.prepared_path, index=False)
            print(f"Prepared data saved to: {self.prepared_path}")
        except Exception as e:
            print(f"WARNING: Failed to save prepared data: {str(e)}")

    def analyze_sentiment(self):
        """
        Perform sentiment analysis using VADER.
        Adds 'sentiment_score' and 'sentiment_label'.
        """
        print("\n[2/2] Running VADER Sentiment Analysis...")
        
        # Download VADER lexicon
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
            
        self.sia = SentimentIntensityAnalyzer()

        def get_vader_score(text):
            # VADER works best on raw text (handles emojis, caps, etc.)
            # So we use the original 'review_text' instead of the processed one
            return self.sia.polarity_scores(str(text))['compound']

        def get_sentiment_label(score):
            if score >= 0.05:
                return 'positive'
            elif score <= -0.05:
                return 'negative'
            else:
                return 'neutral'

        # Calculate scores
        print("Calculating sentiment scores...")
        self.df['sentiment_score'] = self.df['review_text'].apply(get_vader_score)
        
        # Assign labels
        self.df['sentiment_label'] = self.df['sentiment_score'].apply(get_sentiment_label)
        
        # Print distribution
        print("\nSentiment Distribution:")
        print(self.df['sentiment_label'].value_counts(normalize=True) * 100)

    def save_results(self):
        """Save final sentiment results"""
        print("\nSaving sentiment results...")
        try:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            self.df.to_csv(self.output_path, index=False)
            print(f"Results saved to: {self.output_path}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to save results: {str(e)}")
            return False

    def run_pipeline(self):
        """Run the full sentiment analysis pipeline"""
        print("="*60)
        print("STARTING SENTIMENT ANALYSIS PIPELINE")
        print("="*60)
        
        if not self.load_data():
            return False
            
        self.preprocess_for_sentiment()
        self.analyze_sentiment()
        
        if self.save_results():
            print("\n✓ Sentiment analysis completed successfully!")
            return True
        else:
            print("\n✗ Sentiment analysis failed during save.")
            return False

if __name__ == "__main__":
    analyzer = SentimentAnalysis()
    analyzer.run_pipeline()
