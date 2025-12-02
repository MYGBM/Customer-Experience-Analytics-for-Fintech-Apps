Customer Experience Analytics Report for Fintech Apps

Prepared for: Omega Consultancy  
Date: November 30, 2025  
Subject: Analysis of Mobile Banking App Reviews for Customer Retention & Satisfaction

________________________________________

1. Executive Summary

This report outlines the technical implementation and analytical findings of the Customer Experience Analytics project. The objective was to analyze user reviews from the Google Play Store for key Ethiopian banking apps (CBE, Abyssinia, Dashen) to identify drivers of customer satisfaction and retention.

We successfully deployed a data pipeline that scrapes, cleans, and analyzes user sentiment. The analysis reveals a strong correlation between user star ratings and textual sentiment, validating the use of automated sentiment scoring to monitor customer health. This system provides Omega Consultancy with a scalable tool to detect "pain points" (e.g., crashes, login issues) and "satisfaction drivers" (e.g., ease of use) in real-time.

________________________________________

2. Technical Methodology & Pipeline

To achieve the business objectives, we developed a modular Python-based pipeline consisting of three core stages:

Data Collection (Scraping)
Using the google-play-scraper library, we targeted mobile banking applications for Commercial Bank of Ethiopia (CBE), Bank of Abyssinia, and Dashen Bank. We automated the extraction of user reviews, capturing critical metadata including review text, star rating, date, and thumbs-up counts. This resulted in a raw dataset of user feedback representing the "Voice of the Customer."

Data Preprocessing
Implemented in src/preprocessing.py, this stage involved cleaning and deduplication to ensure statistical accuracy. We filtered out non-English (Amharic) characters to ensure compatibility with standard NLP tools while preserving the integrity of English-language feedback. The outcome was a clean, structured dataset ready for Natural Language Processing (NLP).

Sentiment Analysis Pipeline
We utilized the NLTK VADER engine, optimized for social media and short-text reviews. The text preparation in src/sentiment.py involved tokenization and lemmatization to reduce words to their base forms. Crucially, we customized standard stopword lists to explicitly preserve negation words (e.g., "not", "no", "nor"), ensuring accurate sentiment detection (e.g., "not good" is negative). We calculated a "Compound Score" ranging from -1 (Most Negative) to +1 (Most Positive) for every review, enriching the dataset with sentiment scores and labels.

________________________________________

3. Analysis & Findings

The analysis yielded the following insights:

Sentiment Distribution
We categorized reviews into Positive, Neutral, and Negative buckets. This distribution allows us to benchmark the overall "health" of each app. A high ratio of negative sentiment indicates urgent stability or usability issues, serving as a high-level KPI for customer satisfaction.

Sentiment vs. Star Rating Alignment
We found a clear positive correlation between user star ratings and VADER sentiment scores. 1-2 star reviews consistently showed negative scores, while 5-star reviews showed high positive scores. The pipeline can identify "mismatched" reviews (e.g., 5-star rating with negative text), which are high-value targets for product teams.

Bank-Specific Performance
Visualizing "Mean Sentiment Score by Star Rating per Bank" allows for direct competitor analysis. We can compare the intensity of dissatisfaction for 1-star reviews across different banks, identifying where users express significantly more severe frustration.

________________________________________

4. Business Impact & Recommendations

This analytics framework directly supports Omega Consultancy’s goal of improving retention through actionable data.

Enhancing Customer Retention
By monitoring sentiment trends, banks can detect negative spikes caused by buggy updates before they lead to mass churn. We recommend integrating this pipeline into a weekly dashboard to trigger alerts if negative sentiment exceeds a threshold.

Identifying Pain Points & Drivers
The "Negative" sentiment bucket isolates reviews mentioning bugs, crashes, or UI issues. Product teams should focus on high-frequency terms within this cluster to prioritize their roadmap.

Strategic Improvements
Comparing sentiment scores against competitors highlights market position. If a competitor has a higher sentiment score for specific features, the bank should invest in improvements to match market expectations.

Conclusion
The solution transforms raw text into structured metrics, moving banks from reactive guessing to proactive, data-driven decision-making.

________________________________________

5. Challenges & Limitations

Language Nuances: Many reviews use "Amharic-English" transliteration or code-switching, which standard models may misinterpret.
Contextual Sarcasm: VADER struggles with subtle sarcasm, potentially misclassifying it.
Data Imbalance: Reviews are often polarized, leading to fewer neutral examples.

________________________________________

6. Next Steps

Phase 2: Thematic Analysis
Objective: Understand why users feel a certain way.
Action: Implement keyword extraction (TF-IDF/spaCy) to cluster feedback into themes like "Transaction Performance" or "User Interface".
Deliverable: A categorized dataset identifying 3-5 specific themes per bank.

Phase 3: Data Engineering
Objective: Establish persistent storage.
Action: Design and deploy a PostgreSQL database with a relational schema.
Deliverable: A fully populated database with automated ingestion scripts.

Phase 4: Advanced Insights & Visualization
Objective: Synthesize data into strategic recommendations.
Action: Generate comprehensive visualizations and derive specific drivers/pain points.
Deliverable: A final strategic report with evidence-backed recommendations.
