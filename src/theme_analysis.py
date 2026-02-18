"""
Theme Analysis Module
Task 3: Thematic Analysis

This script performs thematic analysis on the reviews.
- Preprocessing: Lemmatization & Stopword Removal (NLTK)
- Keyword Extraction (TF-IDF)
- Rule-Based Theme Classification
"""
import pandas as pd
import numpy as np
import sys
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DATA_PATHS

# Download NLTK resources (if not present)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('omw-1.4', quiet=True)

class ThemeAnalyzer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        # Add domain specific stopwords
        self.stop_words.update(['app', 'bank', 'mobile', 'banking', 'ethiopia', 'please', 'thank', 'thanks'])
        
        # Define Rule-Based Themes (Keywords mapped to Themes)
        # We use stems/lemmas here (e.g., 'login' covers 'logins', 'logging')
        self.theme_keywords = {
            'App Performance': [
                'crash', 'slow', 'bug', 'freeze', 'lag', 'close', 'stuck', 'open', 'load', 
                'update', 'install', 'network', 'connection', 'internet', 'fast', 'speed', 
                'performance', 'working', 'work', 'crushed', 'lazy', 'downtime', 'glitch'
            ],
            'Account Access & Security': [
                'login', 'log in', 'sign in', 'password', 'username', 'otp', 'code', 
                'sms', 'verification', 'register', 'signup', 'account', 'access', 
                'blocked', 'locked', 'pin', 'fingerprint', 'face id', 'activation', 'create'
            ],
            'Transactions & Payments': [
                'transfer', 'send', 'money', 'transaction', 'payment', 'pay', 'fund', 
                'deposit', 'withdraw', 'balance', 'credit', 'debit', 'telebirr', 
                'receipt', 'history', 'statement', 'remittance', 'recharge', 'buy'
            ],
            'User Interface (UI/UX)': [
                'interface', 'design', 'look', 'easy', 'simple', 'hard', 'confusing', 
                'navigate', 'user friendly', 'layout', 'color', 'font', 'language', 
                'english', 'amharic', 'menu', 'button', 'screen', 'dark', "ui", "ux"
            ],
            'Customer Service': [
                'support', 'service', 'customer', 'agent', 'staff', 'branch', 'call', 
                'phone', 'help', 'response', 'contact', 'teller', 'office', 'person'
            ],
            'General Praise': [
                'good', 'great', 'best', 'love', 'like', 'nice', 'excellent', 'amazing', 
                'wonderful', 'perfect', 'thanks', 'thank', 'wow', 'super', 'fine', 'cool', 'satisfied'
            ],
            'General Dissatisfaction': [
                'bad', 'worst', 'terrible', 'horrible', 'hate', 'useless', 'trash', 
                'garbage', 'fake', 'scam', 'poor', 'disappointed', 'annoying', 'stupid'
            ]
        }

    def preprocess_text(self, text):
        """
        Cleans and lemmatizes text:
        1. Lowercase
        2. Remove non-alphabetic characters
        3. Remove stopwords
        4. Lemmatize (running -> run)
        """
        if not isinstance(text, str):
            return ""
        
        # 1. Lowercase & Remove special chars
        #updated the regex  to replace special characters with space
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        
        # 2. Tokenize
        tokens = nltk.word_tokenize(text)
        
        # 3. Remove Stopwords & Lemmatize
        clean_tokens = [
            self.lemmatizer.lemmatize(word) 
            for word in tokens 
            if word.isalpha() and word not in self.stop_words and len(word) > 2
        ]
        
        return " ".join(clean_tokens)

    def assign_theme(self, text):
        """
        Assigns a theme based on keyword matching count.
        Returns the theme with the highest overlap.
        """
        text = str(text) # Ensure string
        scores = {theme: 0 for theme in self.theme_keywords}
        
        # Simple keyword matching
        for theme, keywords in self.theme_keywords.items():
            for keyword in keywords:
                if keyword in text: # 'text' is already lemmatized
                    scores[theme] += 1
        
        # Find max score
        max_theme = max(scores, key=scores.get)
        
        # If no keywords matched (score 0), return Unclassified
        if scores[max_theme] == 0:
            return "General/Unclassified"
        
        return max_theme

    def run_analysis(self):
        print("Loading data...")
        # Load the BERT sentiment results (most recent/accurate data)
        try:
            df = pd.read_csv(DATA_PATHS.get('sentiment_results_bert', DATA_PATHS['sentiment_results_bert']))
        except FileNotFoundError:
            print("BERT results not found, falling back to VADER results...")
            df = pd.read_csv(DATA_PATHS['sentiment_results_bert'])

        print(f"Preprocessing {len(df)} reviews (Lemmatization)...")
        # Create a temporary column for clean text to use in analysis
        df['clean_text'] = df['review_text'].apply(self.preprocess_text)
        
        print("Extracting Keywords (TF-IDF) for validation...")
        # We run TF-IDF just to print top words to console (sanity check)
        tfidf = TfidfVectorizer(max_features=20)
        try:
            tfidf.fit(df['clean_text'])
            print("Top 20 Keywords in Dataset:", tfidf.get_feature_names_out())
        except ValueError:
            print("Not enough text data for TF-IDF.")

        print("Assigning Themes...")
        df['identified_theme'] = df['clean_text'].apply(self.assign_theme)
        
        # Drop the temporary clean_text column if you don't want to save it
        df.drop(columns=['clean_text'], inplace=True)

        output_path = DATA_PATHS['theme_results']
        df.to_csv(output_path, index=False)
        print(f"✅ Theme analysis saved to: {output_path}")

if __name__ == "__main__":
    analyzer = ThemeAnalyzer()
    analyzer.run_analysis()
