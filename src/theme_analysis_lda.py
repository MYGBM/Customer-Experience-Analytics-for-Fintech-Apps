"""
Theme Analysis Module (LDA)
Task 3: Thematic Analysis using Latent Dirichlet Allocation (LDA)

This script performs unsupervised topic modeling on the reviews.
- Preprocessing: Lemmatization & Stopword Removal
- Vectorization: CountVectorizer
- Topic Modeling: LDA (scikit-learn)
"""
import pandas as pd
import numpy as np
import sys
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DATA_PATHS

# Download NLTK resources
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('omw-1.4', quiet=True)

class ThemeAnalyzerLDA:
    def __init__(self, n_topics=6):
        self.n_topics = n_topics
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        # Add domain specific stopwords
        self.stop_words.update(['app', 'bank', 'mobile', 'banking', 'ethiopia', 'please', 'thank', 'thanks'])
        
        self.vectorizer = CountVectorizer(
            max_df=0.95, 
            min_df=2, 
            stop_words=list(self.stop_words),
            ngram_range=(1, 2)
        )
        self.lda_model = LatentDirichletAllocation(
            n_components=self.n_topics,
            max_iter=10,
            learning_method='online',
            random_state=42,
            n_jobs=-1
        )

    def preprocess_text(self, text):
        """
        Cleans and lemmatizes text for LDA
        """
        if not isinstance(text, str):
            return ""
        
        # 1. Lowercase & Remove special chars
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        # 2. Tokenize
        tokens = text.split()
        
        # 3. Remove Stopwords & Lemmatize
        clean_tokens = [
            self.lemmatizer.lemmatize(word) 
            for word in tokens 
            if word not in self.stop_words and len(word) > 2
        ]
        
        return " ".join(clean_tokens)

    def run_analysis(self):
        print("Loading data...")
        try:
            df = pd.read_csv(DATA_PATHS.get('sentiment_results', DATA_PATHS['sentiment_results']))
        except FileNotFoundError:
            print("BERT results not found, falling back to VADER results...")
            df = pd.read_csv(DATA_PATHS['sentiment_results'])

        # Drop NaNs
        df = df.dropna(subset=['review_text'])

        print(f"Preprocessing {len(df)} reviews (Lemmatization)...")
        tqdm.pandas(desc="Preprocessing")
        df['clean_text'] = df['review_text'].progress_apply(self.preprocess_text)
        
        # Filter out empty rows after preprocessing
        df = df[df['clean_text'].str.len() > 0]

        print("Vectorizing text...")
        dtm = self.vectorizer.fit_transform(df['clean_text'])
        
        print(f"Running LDA with {self.n_topics} topics...")
        self.lda_model.fit(dtm)
        
        # Display Topics
        print("\nTop words per topic:")
        feature_names = self.vectorizer.get_feature_names_out()
        topic_keywords = []
        
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_features_ind = topic.argsort()[:-11:-1]
            top_features = [feature_names[i] for i in top_features_ind]
            topic_name = f"Topic {topic_idx}"
            print(f"{topic_name}: {', '.join(top_features)}")
            topic_keywords.append(", ".join(top_features))

        print("\nAssigning Dominant Topics...")
        # Get topic probability distribution for all documents
        topic_results = self.lda_model.transform(dtm)
        
        # Assign dominant topic
        df['topic_id'] = topic_results.argmax(axis=1)
        df['topic_confidence'] = topic_results.max(axis=1)
        
        # Map Topic ID to a string label (Topic 0, Topic 1...)
        # In a real scenario, you'd manually label these after inspection
        df['identified_topic'] = df['topic_id'].apply(lambda x: f"Topic {x}")
        
        # Save keywords for reference (optional, maybe in a separate file or log)
        
        output_path = DATA_PATHS['theme_results_lda']
        df.to_csv(output_path, index=False)
        print(f"✅ LDA Theme analysis saved to: {output_path}")
        
        return df

if __name__ == "__main__":
    analyzer = ThemeAnalyzerLDA(n_topics=6)
    analyzer.run_analysis()
