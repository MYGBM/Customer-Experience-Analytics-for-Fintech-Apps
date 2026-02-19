"""
Theme Analysis Module (LDA — Per-Bank)
Task 3: Thematic Analysis using Latent Dirichlet Allocation (LDA)

Runs LDA separately for each bank to extract bank-specific topics.
- Preprocessing: Lemmatization & Stopword Removal
- Vectorization: CountVectorizer (unigrams + bigrams)
- Topic Modeling: LDA (scikit-learn), one model per bank
- Coherence Scoring: gensim CoherenceModel (c_v) for n_topics tuning
"""
import pandas as pd
import numpy as np
import sys
import os
import re
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DATA_PATHS

# Download NLTK resources
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

class ThemeAnalyzerLDA:
    def __init__(self, n_topics=5):
        self.n_topics = n_topics
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        # Domain-specific stopwords (bank/app generic terms)
        self.stop_words.update(['app', 'bank', 'mobile', 'banking', 'ethiopia', 'please', 'thank', 'thanks'])
        # Conservative set of high-frequency but semantically empty words
        self.stop_words.update(['use', 'get', 'one', 'even', 'also', 'would', 'much', 'really', 'still', 'thing'])

    @staticmethod
    def _get_wordnet_pos(tag):
        """Map NLTK POS tag to WordNet POS for accurate lemmatization."""
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def preprocess_text(self, text):
        """
        Cleans and lemmatizes text for LDA with POS-aware lemmatization.
        """
        if not isinstance(text, str):
            return ""

        # 1. Lowercase & Remove special chars
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())

        # 2. Tokenize
        tokens = nltk.word_tokenize(text)

        # 3. Filter by stopwords and length first
        filtered = [w for w in tokens if w.isalpha() and w not in self.stop_words and len(w) > 2]

        # 4. POS-tag for accurate lemmatization (e.g. 'working' → 'work')
        tagged = pos_tag(filtered)

        # 5. Lemmatize with correct POS
        clean_tokens = [
            self.lemmatizer.lemmatize(word, self._get_wordnet_pos(tag))
            for word, tag in tagged
        ]

        return " ".join(clean_tokens)

    def _fit_lda_for_bank(self, bank_texts, n_topics=None):
        """
        Fits a CountVectorizer + LDA model on a single bank's texts.
        Returns (vectorizer, lda_model, dtm).
        """
        n = n_topics or self.n_topics

        vectorizer = CountVectorizer(
            max_df=0.95,
            min_df=2,
            stop_words=list(self.stop_words),
            ngram_range=(1, 2)
        )
        dtm = vectorizer.fit_transform(bank_texts)

        lda_model = LatentDirichletAllocation(
            n_components=n,
            max_iter=10,
            learning_method='online',
            random_state=42,
            n_jobs=-1
        )
        lda_model.fit(dtm)

        return vectorizer, lda_model, dtm

    def compute_coherence(self, bank_texts, n_topics=None):
        """
        Fits LDA and computes the c_v coherence score for a set of texts.
        Used for tuning the optimal number of topics.
        Returns the coherence score (float).
        """
        vectorizer, lda_model, dtm = self._fit_lda_for_bank(bank_texts, n_topics)

        # Extract top 10 words per topic as a list of lists (gensim format)
        feature_names = vectorizer.get_feature_names_out()
        topics_words = []
        for topic in lda_model.components_:
            top_indices = topic.argsort()[:-11:-1]
            topics_words.append([feature_names[i] for i in top_indices])

        # Build gensim Dictionary and corpus from the tokenized texts
        tokenized = [text.split() for text in bank_texts]
        dictionary = Dictionary(tokenized)

        # Compute c_v coherence
        coherence_model = CoherenceModel(
            topics=topics_words,
            texts=tokenized,
            dictionary=dictionary,
            coherence='c_v'
        )
        return coherence_model.get_coherence()

    def find_optimal_topics(self, df, topic_range=range(2, 11)):
        """
        For each bank, evaluates coherence across a range of n_topics values.
        Returns a dict: {bank_name: {n_topics: coherence_score, ...}, ...}
        """
        results = {}
        banks = df['bank_name'].unique()

        for bank in banks:
            print(f"\n{'='*50}")
            print(f"  Tuning n_topics for: {bank}")
            print(f"{'='*50}")
            bank_texts = df[df['bank_name'] == bank]['clean_text'].tolist()
            bank_results = {}

            for n in topic_range:
                score = self.compute_coherence(bank_texts, n_topics=n)
                bank_results[n] = score
                print(f"  n_topics={n:2d}  →  coherence (c_v) = {score:.4f}")

            best_n = max(bank_results, key=bank_results.get)
            print(f"  ➤ Best n_topics for {bank}: {best_n} (c_v = {bank_results[best_n]:.4f})")
            results[bank] = bank_results

        return results

    def run_analysis(self, n_topics_per_bank=None):
        """
        Runs LDA topic modeling separately for each bank.

        Args:
            n_topics_per_bank: Optional dict mapping bank name to its optimal
                               n_topics, e.g. {'CBE': 4, 'Abyssinia': 5, 'Dashen': 3}.
                               If None, uses self.n_topics for all banks.

        Returns:
            DataFrame with columns: topic_id, topic_confidence, identified_topic
        """
        print("Loading data...")
        try:
            df = pd.read_csv(DATA_PATHS.get('sentiment_results_twitter', DATA_PATHS['sentiment_results_twitter']))
        except FileNotFoundError:
            print("Twitter results not found, falling back to processed reviews...")
            df = pd.read_csv(DATA_PATHS['processed_reviews'])

        # Drop NaNs
        df = df.dropna(subset=['review_text'])
        total_before = len(df)

        print(f"Preprocessing {total_before} reviews (POS-aware Lemmatization)...")
        tqdm.pandas(desc="Preprocessing")
        df['clean_text'] = df['review_text'].progress_apply(self.preprocess_text)

        # Filter out empty rows after preprocessing
        df = df[df['clean_text'].str.len() > 0]
        total_after = len(df)
        dropped = total_before - total_after

        print(f"\n  Preprocessing summary:")
        print(f"    Before: {total_before} reviews")
        print(f"    After:  {total_after} reviews ({dropped} dropped as empty)")
        for bank in df['bank_name'].unique():
            count = len(df[df['bank_name'] == bank])
            print(f"    {bank}: {count} reviews")

        # --- Per-bank LDA ---
        banks = df['bank_name'].unique()
        all_results = []

        for bank in banks:
            bank_df = df[df['bank_name'] == bank].copy()
            n = (n_topics_per_bank or {}).get(bank, self.n_topics)

            print(f"\n{'='*50}")
            print(f"  LDA for {bank}  ({len(bank_df)} reviews, {n} topics)")
            print(f"{'='*50}")

            vectorizer, lda_model, dtm = self._fit_lda_for_bank(
                bank_df['clean_text'], n_topics=n
            )

            # Display top words per topic
            feature_names = vectorizer.get_feature_names_out()
            for topic_idx, topic in enumerate(lda_model.components_):
                top_features_ind = topic.argsort()[:-11:-1]
                top_features = [feature_names[i] for i in top_features_ind]
                print(f"  Topic {topic_idx}: {', '.join(top_features)}")

            # Assign dominant topic
            topic_results = lda_model.transform(dtm)
            bank_df['topic_id'] = topic_results.argmax(axis=1)
            bank_df['topic_confidence'] = topic_results.max(axis=1)
            bank_df['identified_topic'] = bank_df['topic_id'].apply(
                lambda x: f"{bank}_Topic_{x}"
            )

            all_results.append(bank_df)

        # Combine all banks
        df_final = pd.concat(all_results, ignore_index=True)

        output_path = DATA_PATHS['theme_results_lda']
        df_final.to_csv(output_path, index=False)
        print(f"\n✅ Per-bank LDA theme analysis saved to: {output_path}")
        print(f"   Total reviews: {len(df_final)}")
        for bank in banks:
            count = len(df_final[df_final['bank_name'] == bank])
            print(f"   {bank}: {count} reviews")

        return df_final

if __name__ == "__main__":
    analyzer = ThemeAnalyzerLDA(n_topics=5)
    analyzer.run_analysis()
