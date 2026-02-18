"""
Sentiment Evaluation Module
Shared evaluation function for comparing predicted sentiment labels against star ratings.

Ground truth mapping:
  1-2 stars → negative
  3 stars   → neutral
  4-5 stars → positive
"""

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score


def star_to_sentiment(rating):
    """Convert star rating to ground truth sentiment label."""
    if rating <= 2:
        return 'negative'
    elif rating == 3:
        return 'neutral'
    else:
        return 'positive'


def evaluate_sentiment(df, model_name="Model"):
    """
    Evaluate sentiment predictions against star-rating ground truth.
    
    Args:
        df: DataFrame with columns 'rating', 'sentiment_score', 'sentiment_label'
        model_name: Name of the model for display purposes
        
    Returns:
        dict with evaluation metrics
    """
    # Make a copy to avoid modifying the original
    eval_df = df.dropna(subset=['rating', 'sentiment_score', 'sentiment_label']).copy()
    
    # Create ground truth from star ratings
    eval_df['ground_truth'] = eval_df['rating'].apply(star_to_sentiment)
    
    # --- 3 Essential Metrics ---
    
    # 1. Overall Accuracy
    accuracy = accuracy_score(eval_df['ground_truth'], eval_df['sentiment_label'])
    
    # 2. Full classification report (all 9 per-class metrics)
    labels = ['negative', 'neutral', 'positive']
    report = classification_report(
        eval_df['ground_truth'], 
        eval_df['sentiment_label'], 
        labels=labels,
        output_dict=True,
        zero_division=0
    )
    report_str = classification_report(
        eval_df['ground_truth'], 
        eval_df['sentiment_label'], 
        labels=labels,
        zero_division=0
    )
    
    # 3. Negative Recall (most important single metric)
    negative_recall = report['negative']['recall']
    
    # 4. Pearson Correlation (sentiment_score vs rating)
    correlation = eval_df['sentiment_score'].corr(eval_df['rating'])
    
    # --- Print Summary ---
    print(f"\n{'='*60}")
    print(f"SENTIMENT EVALUATION: {model_name}")
    print(f"{'='*60}")
    print(f"Reviews evaluated: {len(eval_df)}")
    print(f"\n--- 3 Essential Metrics ---")
    print(f"  Overall Accuracy:      {accuracy:.1%}")
    print(f"  Negative Recall:       {negative_recall:.1%}    ← Did we catch the complaints?")
    print(f"  Score-Rating Corr:     {correlation:.3f}")
    print(f"\n--- Full Classification Report ---")
    print(report_str)
    
    return {
        'accuracy': accuracy,
        'negative_recall': negative_recall,
        'correlation': correlation,
        'report': report,
        'report_str': report_str,
        'n_evaluated': len(eval_df)
    }
