"""
BERT Sentiment Analysis Module
Task 2: Advanced Sentiment Analysis

This script performs sentiment analysis using a pre-trained DistilBERT model via Hugging Face Pipelines.
- Model: distilbert-base-uncased-finetuned-sst-2-english
- Implementation: Uses 'pipeline' with KeyDataset for efficient GPU batch processing.
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

class BertSentimentAnalysis:
    """Pipeline for sentiment analysis using Hugging Face Transformers (DistilBERT)"""

    def __init__(self):
        self.input_path = DATA_PATHS['processed_reviews']
        self.output_path = DATA_PATHS['sentiment_results_bert']
        # Check for GPU
        self.device = 0 if torch.cuda.is_available() else -1
        print(f"🚀 Using device: {'GPU (cuda:0)' if self.device == 0 else 'CPU'}")
        
        # Initialize Pipeline
        # Defaults to distilbert-base-uncased-finetuned-sst-2-english
        print("Loading Sentiment Analysis Pipeline...")
        self.pipe = pipeline(
            task="sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=self.device
        )

    def run_pipeline(self):
        """Runs the full sentiment analysis pipeline"""
        print("="*60)
        print("STARTING BERT SENTIMENT ANALYSIS PIPELINE")
        print("="*60)

        # 1. Load Data using 'datasets' for efficiency
        print(f"Loading data from: {self.input_path}")
        try:
            # Load CSV directly into a Dataset object
            # split="train" loads it as a Dataset instead of DatasetDict
            dataset = load_dataset("csv", data_files=self.input_path, split="train")
            
            # Preprocess: Demojize text to handle emojis
            print("Preprocessing: Converting emojis to text...")
            def demojize_text(example):
                # Handle None/NaN values
                text = example['review_text'] if example['review_text'] is not None else ""
                example['review_text'] = emoji.demojize(str(text), delimiters=(" ", " "))
                return example

            dataset = dataset.map(demojize_text)
            print(f"✅ Loaded and preprocessed {len(dataset)} reviews.")
        except Exception as e:
            print(f"❌ Failed to load data: {e}")
            return False

        # 2. Run Inference
        print("Running inference on GPU...")
        results = []
        
        # Use KeyDataset to stream 'review_text' column efficiently
        # Batch size 64 is good for RTX 4070
        try:
            for out in tqdm(self.pipe(KeyDataset(dataset, "review_text"), batch_size=64, truncation=True, padding=True, max_length=512), total=len(dataset)):
                results.append(out)
        except Exception as e:
            print(f"❌ Inference failed: {e}")
            return False

        # 3. Process Results (Calculate Scores & Labels)
        print("Processing scores...")
        
        # Read original CSV to DataFrame to append results
        df = pd.read_csv(self.input_path)
        
        sentiment_scores = []
        sentiment_labels = []
        
        for res in results:
            # res looks like {'label': 'POSITIVE', 'score': 0.998}
            label = res['label']
            score = res['score']
            
            # Map to continuous score (-1 to 1)
            # If POSITIVE, score is +confidence
            # If NEGATIVE, score is -confidence
            final_score = score if label == 'POSITIVE' else -score
            
            sentiment_scores.append(final_score)
            
            # Assign Label based on Thresholds (Wider than VADER)
            if final_score > 0.2:
                final_label = 'positive'
            elif final_score < -0.2:
                final_label = 'negative'
            else:
                final_label = 'neutral'
            
            sentiment_labels.append(final_label)

        df['sentiment_score'] = sentiment_scores
        df['sentiment_label'] = sentiment_labels
        
        # 4. Save Results
        print(f"Saving results to: {self.output_path}")
        try:
            df.to_csv(self.output_path, index=False)
            print("✅ Results saved successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return False

if __name__ == "__main__":
    analyzer = BertSentimentAnalysis()
    analyzer.run_pipeline()