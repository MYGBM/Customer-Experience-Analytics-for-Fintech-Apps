"""
Sentiment Analysis Module (VADER)
Task 2: Sentiment Analysis Pipeline

This script performs sentiment analysis on the preprocessed reviews using VADER.
VADER works best on raw text — it handles emojis, capitalization, and punctuation natively.
"""

import sys
import os
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DATA_PATHS
from src.sentiment_evaluation import evaluate_sentiment


class SentimentAnalysis:
    """Pipeline for sentiment analysis using NLTK VADER"""

    def __init__(self, input_path=None, output_path=None):
        """
        Initialize the sentiment analysis pipeline
        
        Args:
            input_path (str): Path to processed reviews CSV
            output_path (str): Path to save final sentiment results
        """
        self.input_path = input_path or DATA_PATHS['processed_reviews']
        self.output_path = output_path or DATA_PATHS['sentiment_results_vader']
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

    def analyze_sentiment(self):
        """
        Perform sentiment analysis using VADER.
        VADER runs on raw review_text — no preprocessing needed.
        Adds 'sentiment_score' and 'sentiment_label'.
        """
        print("\n[1/3] Running VADER Sentiment Analysis...")
        
        # Download VADER lexicon
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
            
        self.sia = SentimentIntensityAnalyzer()

        def get_vader_score(text):
            # VADER works best on raw text (handles emojis, caps, etc.)
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

        # Per-bank sentiment summary
        if 'bank_name' in self.df.columns and 'rating' in self.df.columns:
            print("\nPer-Bank Mean Sentiment Score by Star Rating:")
            summary = self.df.groupby(['bank_name', 'rating'])['sentiment_score'].mean().unstack(fill_value=0)
            print(summary.round(3))

    def evaluate(self):
        """Evaluate sentiment predictions against star-rating ground truth."""
        print("\n[2/3] Evaluating sentiment predictions...")
        if 'rating' not in self.df.columns:
            print("WARNING: 'rating' column not found — skipping evaluation.")
            return
        return evaluate_sentiment(self.df, model_name="VADER")

    def save_results(self):
        """Save final sentiment results"""
        print("\n[3/3] Saving sentiment results...")
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
        print("STARTING VADER SENTIMENT ANALYSIS PIPELINE")
        print("="*60)
        
        if not self.load_data():
            return False
            
        self.analyze_sentiment()
        self.evaluate()
        
        if self.save_results():
            print("\n✓ VADER sentiment analysis completed successfully!")
            return True
        else:
            print("\n✗ Sentiment analysis failed during save.")
            return False

if __name__ == "__main__":
    analyzer = SentimentAnalysis()
    analyzer.run_pipeline()
