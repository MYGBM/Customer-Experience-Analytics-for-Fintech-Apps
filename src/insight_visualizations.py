"""
Insight Visualizations Module
Reusable chart functions for Task 4: Insights & Recommendations.

All functions accept a DataFrame (from reviews_with_themes_lda.csv)
and return the matplotlib Figure so callers can show or save it.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
from nltk.corpus import stopwords


# ──────────────────────────────────────────────
# Palette & style helpers
# ──────────────────────────────────────────────

BANK_PALETTE = {
    'Commercial Bank of Ethiopia': '#1f77b4',
    'Abyssinia Bank': '#ff7f0e',
    'Dashen Bank': '#2ca02c',
}

# Consolidated stop word set (same as LDA preprocessing + extras)
_STOP_WORDS = set(stopwords.words('english'))
_STOP_WORDS.update([
    'app', 'bank', 'mobile', 'banking', 'ethiopia', 'please', 'thank', 'thanks',
    'use', 'get', 'one', 'even', 'also', 'would', 'much', 'really', 'still', 'thing',
    'good', 'great', 'nice', 'best', 'like', 'well', 'make', 'want', 'need', 'time',
    'work', 'try', 'say', 'new', 'way', 'day', 'come', 'know', 'go', 'many', 'good', 'worse', 'worst', 'easy', 'bad', 'dashen', 'cbe', 'abyssinia'
])


def _sentiment_color(val):
    """Return green for positive sentiment, red for negative."""
    return '#2ecc71' if val >= 0 else '#e74c3c'


def _bank_list(df):
    """Return sorted unique bank names."""
    return sorted(df['bank_name'].dropna().unique())


# ──────────────────────────────────────────────
# 1. Theme Distribution by Bank
# ──────────────────────────────────────────────

def plot_theme_distribution(df, figsize=(13, 6)):
    """Horizontal stacked bar chart showing theme share (%) per bank."""
    theme_counts = df.groupby(['bank_name', 'theme']).size().reset_index(name='count')
    total_by_bank = df.groupby('bank_name').size().reset_index(name='total')
    theme_counts = theme_counts.merge(total_by_bank, on='bank_name')
    theme_counts['percentage'] = (theme_counts['count'] / theme_counts['total']) * 100

    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(
        data=theme_counts, y='bank_name', x='percentage',
        hue='theme', orient='h', ax=ax,
    )
    ax.set_title('Theme Distribution by Bank', fontsize=14, fontweight='bold')
    ax.set_xlabel('Percentage of Reviews')
    ax.set_ylabel('')
    ax.legend(title='Theme', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    fig.tight_layout()
    return fig


# ──────────────────────────────────────────────
# 2. Top Themes by Sentiment — PER BANK
# ──────────────────────────────────────────────

def plot_theme_sentiment_bars(df, figsize=(14, 5)):
    """
    One subplot per bank: sorted horizontal bar chart of mean sentiment
    per theme. Green = driver, red = pain point.
    """
    banks = _bank_list(df)
    fig, axes = plt.subplots(1, len(banks), figsize=(figsize[0], figsize[1]),
                             sharey=False)
    if len(banks) == 1:
        axes = [axes]

    for ax, bank in zip(axes, banks):
        bdf = df[df['bank_name'] == bank]
        theme_sent = (
            bdf.groupby('theme')['sentiment_score']
            .mean()
            .sort_values()
            .reset_index()
        )
        theme_sent.columns = ['theme', 'mean_sentiment']
        colors = [_sentiment_color(v) for v in theme_sent['mean_sentiment']]
        ax.barh(theme_sent['theme'], theme_sent['mean_sentiment'], color=colors)
        ax.axvline(0, color='grey', linewidth=0.8, linestyle='--')
        ax.set_title(bank, fontsize=11, fontweight='bold')
        ax.set_xlabel('Mean Sentiment')

    fig.suptitle('Top Themes by Sentiment per Bank (Pain Points ← → Drivers)',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    return fig


# ──────────────────────────────────────────────
# 3. Sentiment Heatmap — PER BANK (side-by-side)
# ──────────────────────────────────────────────

def plot_sentiment_heatmap(df, figsize=(16, 5)):
    """
    One heatmap subplot per bank: theme (rows) × sentiment stats.
    Uses a single-bank pivot so each bank's themes are visible even
    when they don't overlap with other banks.
    """
    banks = _bank_list(df)
    fig, axes = plt.subplots(1, len(banks), figsize=(figsize[0], figsize[1]))
    if len(banks) == 1:
        axes = [axes]

    for ax, bank in zip(axes, banks):
        bdf = df[df['bank_name'] == bank]
        pivot = (
            bdf.groupby('theme')['sentiment_score']
            .mean()
            .to_frame()
        )
        pivot.columns = ['Mean Sentiment']
        sns.heatmap(
            pivot, annot=True, fmt='.2f', cmap='RdYlGn', center=0,
            linewidths=0.5, vmin=-1, vmax=1, ax=ax, cbar=False,
        )
        ax.set_title(bank, fontsize=11, fontweight='bold')
        ax.set_ylabel('')

    fig.suptitle('Mean Sentiment by Theme per Bank', fontsize=13, fontweight='bold')
    fig.tight_layout()
    return fig


# ──────────────────────────────────────────────
# 4. Word Clouds per Bank (stop words removed)
# ──────────────────────────────────────────────

def plot_wordclouds(df, figsize=(18, 5)):
    """One word cloud per bank from clean_text, with stop words removed."""
    banks = _bank_list(df)
    fig, axes = plt.subplots(1, len(banks), figsize=figsize)
    if len(banks) == 1:
        axes = [axes]

    for ax, bank in zip(axes, banks):
        text = ' '.join(df.loc[df['bank_name'] == bank, 'clean_text'].dropna())
        wc = WordCloud(
            width=600, height=400,
            background_color='white',
            colormap='viridis',
            max_words=80,
            stopwords=_STOP_WORDS,
        ).generate(text)
        ax.imshow(wc, interpolation='bilinear')
        ax.set_title(bank, fontsize=13, fontweight='bold')
        ax.axis('off')

    fig.suptitle('Most Frequent Words per Bank', fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout()
    return fig


# ──────────────────────────────────────────────
# 5. Priority Scatter — PER BANK (subplots)
# ──────────────────────────────────────────────

def plot_priority_scatter(df, figsize=(16, 5)):
    """
    One subplot per bank: x = mean sentiment, y = review count per theme.
    Top-left quadrant = highest-priority pain points.
    """
    banks = _bank_list(df)
    fig, axes = plt.subplots(1, len(banks), figsize=(figsize[0], figsize[1]),
                             sharey=False)
    if len(banks) == 1:
        axes = [axes]

    for ax, bank in zip(axes, banks):
        bdf = df[df['bank_name'] == bank]
        summary = (
            bdf.groupby('theme')
            .agg(count=('theme', 'size'),
                 mean_sentiment=('sentiment_score', 'mean'))
            .reset_index()
        )
        color = BANK_PALETTE.get(bank, '#333')
        ax.scatter(
            summary['mean_sentiment'], summary['count'],
            s=summary['count'] * 3, alpha=0.7, color=color,
        )
        for _, row in summary.iterrows():
            label = row['theme']
            if len(label) > 28:
                label = label[:26] + '…'
            ax.annotate(
                label,
                (row['mean_sentiment'], row['count']),
                fontsize=7, ha='center', va='bottom',
            )
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        ax.set_title(bank, fontsize=11, fontweight='bold')
        ax.set_xlabel('Mean Sentiment')
        ax.set_ylabel('# Reviews')

    fig.suptitle('Theme Priority: Volume vs Sentiment per Bank',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    return fig


# ──────────────────────────────────────────────
# 7. Sentiment Boxplot by Theme per Bank
# ──────────────────────────────────────────────

def plot_sentiment_boxplot(df, figsize=(18, 6)):
    """
    One subplot per bank: box-and-whisker plot of sentiment_score
    distribution grouped by theme. Reveals spread, outliers, and
    median shifts that summary statistics (mean bars) can hide.
    """
    banks = _bank_list(df)
    fig, axes = plt.subplots(1, len(banks), figsize=(figsize[0], figsize[1]),
                             sharey=True)
    if len(banks) == 1:
        axes = [axes]

    for ax, bank in zip(axes, banks):
        bdf = df[df['bank_name'] == bank].copy()

        # Order themes by median sentiment (lowest first → pain points on top)
        theme_order = (
            bdf.groupby('theme')['sentiment_score']
            .median()
            .sort_values()
            .index
            .tolist()
        )

        color = BANK_PALETTE.get(bank, '#333')
        sns.boxplot(
            data=bdf,
            y='theme',
            x='sentiment_score',
            order=theme_order,
            color=color,
            fliersize=2,
            linewidth=0.8,
            ax=ax,
        )
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        ax.set_title(bank, fontsize=11, fontweight='bold')
        ax.set_xlabel('Sentiment Score')
        ax.set_ylabel('')

    fig.suptitle('Sentiment Distribution by Theme per Bank',
                 fontsize=13, fontweight='bold')
    fig.tight_layout()
    return fig
