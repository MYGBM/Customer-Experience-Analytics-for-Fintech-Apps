"""
Twitter-RoBERTa Sentiment Analysis Module
Task 2: Advanced Sentiment Analysis

This script performs sentiment analysis using cardiffnlp/twitter-roberta-base-sentiment-latest.
- Trained on ~124M tweets, fine-tuned on ~60K sentiment-labeled tweets
- Native 3-class output: negative, neutral, positive (no manual thresholds)
- Handles emojis, slang, and short text well
"""

import sys
import os
import torch
import pandas as pd
import emoji
from tqdm import tqdm
from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset
from datasets import load_dataset

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DATA_PATHS
from src.sentiment_evaluation import evaluate_sentiment




class TwitterSentimentAnalysis:
    """Pipeline for sentiment analysis using Twitter-RoBERTa"""

    def __init__(self):
        self.input_path = DATA_PATHS['processed_reviews']
        self.output_path = DATA_PATHS['sentiment_results_twitter']
        # Check for GPU
        self.device = 0 if torch.cuda.is_available() else -1
        print(f"🚀 Using device: {'GPU (cuda:0)' if self.device == 0 else 'CPU'}")
        
        # Initialize Pipeline
        print("Loading Twitter-RoBERTa Sentiment Analysis Pipeline...")
        self.pipe = pipeline(
            task="sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=self.device,
            top_k=None  # Return all 3 class probabilities
        )

    def run_pipeline(self):
        """Runs the full sentiment analysis pipeline"""
        print("="*60)
        print("STARTING TWITTER-ROBERTA SENTIMENT ANALYSIS PIPELINE")
        print("="*60)

        # 1. Load Data using 'datasets' for efficiency
        print(f"\n[1/4] Loading data from: {self.input_path}")
        try:
            dataset = load_dataset("csv", data_files=self.input_path, split="train")
            
            # Preprocess: Demojize text to handle emojis
            print("Preprocessing: Converting emojis to text...")
            def demojize_text(example):
                text = example['review_text'] if example['review_text'] is not None else ""
                example['review_text'] = emoji.demojize(str(text), delimiters=(" ", " "))
                return example

            dataset = dataset.map(demojize_text)
            print(f"✅ Loaded and preprocessed {len(dataset)} reviews.")
        except Exception as e:
            print(f"❌ Failed to load data: {e}")
            return False

        # 2. Run Inference
        print("\n[2/4] Running inference...")
        results = []
        
        try:
            for out in tqdm(
                self.pipe(
                    KeyDataset(dataset, "review_text"), 
                    batch_size=64, 
                    truncation=True, 
                    padding=True, 
                    max_length=512
                ), 
                total=len(dataset)
            ):
                results.append(out)
        except Exception as e:
            print(f"❌ Inference failed: {e}")
            return False

        # 3. Process Results
        print("\n[3/4] Processing scores...")
        
        # Read original CSV to DataFrame to append results
        df = pd.read_csv(self.input_path)
        
        sentiment_scores = []
        sentiment_labels = []
        
        for res in results:
            # res is a list of 3 dicts: [{'label': 'negative', 'score': ...}, ...]
            probs = {item['label']: item['score'] for item in res}
            
            # Score = P(positive) - P(negative), range: -1 to +1
            # Neutral is implicitly captured: when P(neutral) is high,
            # both P(pos) and P(neg) are low, so score is near 0
            score = probs['positive'] - probs['negative']
            sentiment_scores.append(score)
            
            # Label = class with highest probability (no manual threshold)
            label = max(probs, key=probs.get)
            sentiment_labels.append(label)

        df['sentiment_score'] = sentiment_scores
        df['sentiment_label'] = sentiment_labels
        
        # Print distribution
        print("\nSentiment Distribution:")
        print(df['sentiment_label'].value_counts(normalize=True) * 100)

        # Per-bank sentiment summary
        if 'bank_name' in df.columns and 'rating' in df.columns:
            print("\nPer-Bank Mean Sentiment Score by Star Rating:")
            summary = df.groupby(['bank_name', 'rating'])['sentiment_score'].mean().unstack(fill_value=0)
            print(summary.round(3))

        # 4. Evaluate & Save
        print("\n[4/4] Evaluating and saving...")
        if 'rating' in df.columns:
            evaluate_sentiment(df, model_name="Twitter-RoBERTa")

        print(f"\nSaving results to: {self.output_path}")
        try:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            df.to_csv(self.output_path, index=False)
            print("✅ Results saved successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False


if __name__ == "__main__":
    analyzer = TwitterSentimentAnalysis()
    analyzer.run_pipeline()
