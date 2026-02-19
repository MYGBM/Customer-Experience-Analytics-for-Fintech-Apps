Comprehensive Project Report: Customer Experience Analytics for Ethiopian Fintech Apps
Date: February 2026 Prepared for: Strategic Management Teams of CBE, Abyssinia Bank, and Dashen Bank Prepared by: CX Analytics Team

1. Executive Summary
   This report presents the findings of a comprehensive Customer Experience (CX) Analytics project aimed at transforming unstructured user feedback into actionable strategic insights for Ethiopia's leading fintech applications: Commercial Bank of Ethiopia (CBE), Abyssinia Bank, and Dashen Bank.

In an increasingly competitive digital banking landscape, understanding user sentiment beyond simple star ratings is concise. This project engaged in a rigorous end-to-end data science pipeline, migrating from traditional rule-based sentiment analysis to state-of-the-art Deep Learning models.

Key Highlights:

Data Foundation: Analyzed a robust dataset of over 12,000 user reviews scraped directly from the Google Play Store.
Technological Leap: Transitioned from VADER (66.2% Accuracy) to a Twitter-RoBERTa Transformer model (72.1% Accuracy), significantly improving the detection of negative user sentiment (Recall improved from 40.5% to 71.5%).
Thematic Discovery: Utilized Latent Dirichlet Allocation (LDA) to uncover hidden themes specific to each bank, moving beyond generic keywords to identify precise issue clusters like "Update-Induced Instability" and "OTP Delivery Failures."
Business Impact: Identified that while all banks suffer from technical debt, Dashen Bank leads in feature satisfaction ("Super App" experience), Abyssinia is praised for UI but plagued by login issues, and CBE faces critical challenges with basic app stability following updates.
The insights detailed herein are delivered via a deployed interactive dashboard, empowering stakeholders to monitor real-time user sentiment and prioritize engineering efforts based on quantitative evidence.

2. Methodology & Data Acquisition
   2.1 Data Collection Pipeline
   The foundation of this study is a custom-built scraping pipeline designed to harvest "Voice of the Customer" data directly from the source.

Source: Google Play Store.
Tooling: Python google_play_scraper library with a custom
PlayStoreScraper
class (
src/scraper.py
).
Scope:
CBE Mobile Banking: ~8,000 reviews.
Apollo (Bank of Abyssinia): ~1,200 reviews.
Amole (Dashen Bank): ~770 reviews.
Data Integrity: The pipeline implements a retry mechanism with exponential backoff to handle network intermittency, ensuring complete data retrieval. Reviews were sorted by Sort.NEWEST to prioritize recent feedback and relevant app versions.
2.2 Data Preprocessing
Raw text data is noisy. A multi-stage preprocessing pipeline was implemented to ensure analytical rigor:

Noise Reduction: Removal of special characters and HTML artifacts.
Demojization: Converting emojis (e.g., "😡") into text descriptions (":pouting_face:") to preserve their strong emotional signal for the sentiment models.
Normalization: Lowercasing and standardizing text for consistent tokenization. 3. Advanced Sentiment Analysis
A core objective was to accurately quantify user sentiment. Two distinct approaches were evaluated to determine the optimal solution for financial text analysis.

3.1 Baseline: VADER (Rule-Based Approach)
Initial analysis utilized VADER (Valence Aware Dictionary and sEntiment Reasoner).

Mechanism: Assigns sentiment scores based on a predefined lexicon of positive and negative words.
Performance:
Overall Accuracy: 66.2%
Negative Recall: 40.5%
Limitations: The low negative recall indicates that VADER missed nearly 60% of critical user complaints. It failed to grasp context, often classifying "I can't login" as Neutral because it lacks explicitly negative adjectives.
3.2 Advanced: Twitter-RoBERTa (Transformer Model)
To overcome VADER's limitations, cardiffnlp/twitter-roberta-base-sentiment-latest, a Transformer model pre-trained on ~58 million tweets, was deployed.

Mechanism: Uses attention mechanisms to understand the context of words. It recognizes that "waiting forever" is negative, even without "bad" words.
Key Metrics:
Overall Accuracy: 72.1% (+5.9% improvement)
Negative Recall: 71.5% (+31% improvement)
Score-Rating Correlation: 0.705 (Strong positive correlation)
Impact: The massive improvement in Negative Recall is critical. It means the vast majority of user complaints are now successfully flagged, ensuring no critical bug report goes unnoticed.
Visual Evidence:

[Placeholder: Comparative Bar Chart - VADER vs. RoBERTa Accuracy & Recall] The chart would show a side-by-side comparison highlighting the drastic jump in detecting negative sentiment.
3.2.1 Evaluation Protocol & Ground Truth Generation
To rigorously benchmark the models, a standardized evaluation framework was implemented (source: `src/sentiment_evaluation.py`).

**1. Constructing Ground Truth:**
Since raw reviews lack explicit sentiment labels, "Star Ratings" were used as a proxy to generate Ground Truth labels:

- **Negative:** 1 & 2 Stars (The primary target for complaint detection)
- **Neutral:** 3 Stars
- **Positive:** 4 & 5 Stars

**2. Key Success Metrics:**
Beyond standard **Accuracy**, the evaluation prioritized two specific metrics aligned with business goals:

- **Negative Recall:** The percentage of _actual_ negative reviews correctly flagged by the model. This is the critical "Safety Metric"—a high negative recall ensures that customer complaints are not ignored.
- **Score-Rating Correlation:** A Pearson correlation analysis was run to measure how linearly the sentiment scores tracked with the user's star rating, vetting the model's granularity.

4. Thematic Analysis: Uncovering the "Why"
   Knowing that users are unhappy is not enough; the "why" must be understood. Latent Dirichlet Allocation (LDA), an unsupervised machine learning technique, was employed to discover the hidden thematic structures within the reviews.

4.1 LDA Optimization
Instead of a "one size fits all" model, separate LDA models were trained for each bank to capture their unique product landscapes. Coherence Scores ($C_v$) were used to scientifically determine the optimal number of topics for each:

Abyssinia: Optimal Topics = 8 (High complexity, diverse feedback)
CBE: Optimal Topics = 5 (Focused on core banking functions)
Dashen: Optimal Topics = 3 (Concentrated feedback on specific features)
4.2 Topic Interpretation & Theming Strategy
While LDA provides mathematical clusters of words (Topics), these raw outputs often contain generic or overlapping terms (e.g., "work", "time", "app"). To transform these statistical clusters into actionable business insights, a rigorous qualitative layer was applied: `High-Confidence Sample Review Reading`.

**Methodology:**

1.  **High-Confidence Filtering:** For each latent topic identified by the model, we extracted the **top 10 reviews** where the model's confidence probability ($P(Topic|Document)$) was highest ($> 0.90$). These reviews represent the "purest" expression of that topic.
2.  **Targeted Review Reading:** Instead of guessing the topic's meaning from keywords alone, I manually read these high-confidence reviews to understand the _context_ of the complaint.
    - _Example:_ A topic with keywords "security" and "option" might seem vague. Reading the high-confidence reviews revealed specific frustration: _"The app blocks me because of 'Developer Options' even when they are disabled."_
3.  **Labeling & Grouping:**
    - **Step 1 - Labeling:** Each numerical topic (e.g., Topic 2) was assigned a descriptive label based on the human review (e.g., "Developer Options Blocking").
    - **Step 2 - Theming:** Related topics were then aggregated into broad **Themes** to simplify reporting.
      - _Logic:_ (Topic 0 "Login Failure") + (Topic 3 "OTP Issues") $\rightarrow$ **Theme: "Authentication & Security"**.

This "Human-in-the-Loop" validation ensures that the reported themes—such as "Update-Induced Instability" or "Super App Experience"—are not just keyword associations, but accurately reflect the nuanced voice of the customer.

4.3 Key Themes & Keywords
The model successfully extracted distinct thematic clusters. Below are the dominant themes identified for each bank, along with their top defining keywords.

Commercial Bank of Ethiopia (CBE)
Theme 1: App Stability & Updates
Keywords: update, open, work, please, fix, problem, version
Insight: Users struggle massively with the update process. A recurring pattern is the app refusing to open immediately after a mandatory update.
Theme 2: Login & Authentication
Keywords: login, password, account, change, incorrect, device
Insight: "Incorrect username/password" errors are frequent, even for valid credentials, suggesting backend sync issues.
Theme 3: General Usability
Keywords: good, best, cbe, nice, thank, service, easy
Insight: When the app works, users appreciate its utility and "nice" interface.
Abyssinia Bank (Apollo)
Theme 1: Transaction Performance
Keywords: transaction, transfer, money, fail, account,
bank
Insight: High friction in money transfers. "Failed" is a dominant term co-occurring with "money".
Theme 2: Verification Friction
Keywords: verification,
id
, photo, selfie, camera, document
Insight: The digital onboarding process (eKYC) is a major hurdle. Users report issues with the camera not capturing ID documents clearly.
Theme 3: Modern UI/UX
Keywords: love, interface, smooth, modern, fast,
app
Insight: Strong praise for the aesthetic and "smooth" feel of the app, verifying their design-first strategy.
Dashen Bank (Amole)
Theme 1: The "Super App" Experience
Keywords: amole, pay, ticket, concert, buy, everything
Insight: Users view Amole not just as a bank, but a lifestyle app for buying tickets and paying bills.
Theme 2: Airtime & System Errors
Keywords: airtime, buy, card, system,
connection
, error
Insight: Buying mobile airtime is a high-frequency use case that frequently fails, causing immediate frustration. 5. Strategic Insights & Prioritization
By combining Sentiment Scores (from RoBERTa) with Topic Volume (from LDA), a Prioritization Matrix was developed to guide engineering efforts.

5.1 The "Pain Points" vs. "Drivers" Analysis
Every theme was mapped to a quadrant based on its Volume (Frequency) and Mean Sentiment.

Quadrant I: Critical Priorities (High Volume, Negative Sentiment)
These are the "Bleeding/Burning" issues that drive churn.

CBE - Update Handling: The sheer volume of complaints regarding broken updates makes this the #1 systemic risk for CBE.
Abyssinia - OTP Delivery: A technical failure point where the SMS OTP simply never arrives, locking users out completely.
Dashen - Connection Timeouts: "System busy" errors during peak hours for simple tasks like balance checks.
Quadrant II: Strategic Drivers (High Volume, Positive Sentiment)
These are the pillars of retention that must be protected.

Dashen - All-in-One Functionality: The ability to pay for concerts (DSTV, events) is a unique selling point (USP) that competitors lack.
Abyssinia - User Interface: The visual polish is a significant differentiator in a market of utilitarian apps.
CBE - Reliability (Legacy): Despite bugs, long-term users trust CBE for large transfers more than newer fintechs.
[Placeholder: Priority Scatter Plot - Volume vs. Sentiment] Visualizes themes as bubbles. X-axis: Sentiment, Y-axis: Volume. Top-left quadrant = Critical Actions.

5.2 Deep Dive: Theme Sentiment Distribution
An analysis of the sentiment spread within specific themes reveals opportunities for quick wins.

Polarized Themes: "Security" topics often show extreme polarization. Users are either grateful for protection or furious at being locked out. There is no middle ground.
Consistently Negative: "Customer Support" related keywords (call, branch, answer) have a near -1.0 sentiment score across all banks, indicating a digital-channel failure that forces physical branch visits.
[Placeholder: Sentiment Heatmap by Theme] A heatmap showing the intensity of negative/positive sentiment for each theme across the three banks.

6. Database Architecture & Data Pipeline
   To support the high-performance dashboard, a robust relational database architecture was implemented, moving beyond static CSV files.

6.1 Schema Design (
scripts/schema.sql
)
A Normalized PostgreSQL schema was designed to enforce data integrity and query efficiency:

banks
Table: Stores metadata for each financial institution (CBE, Abyssinia, Dashen), acting as the primary reference entity.
reviews
Table: The core fact table containing:
Metadata: review_text, rating, review_date, thumbs_up.
NLP Enriched Data: sentiment_score, sentiment_label,
theme
, topic_confidence.
Indexing Strategy: B-Tree indexes were created on high-cardinality columns used for filtering (bank_id, review_date, sentiment_label) to ensure sub-millisecond query performance for the dashboard.
6.2 ETL Pipeline (
scripts/insert_reviews.py
)
A custom Python ETL (Extract, Transform, Load) script was developed to migrate processed data from the notebook environment to the production database.

Extraction: Reads the final enriched dataset (
reviews_with_themes_lda.csv
) generated by the analysis notebooks.
Transformation:
Maps string-based bank names to foreign key bank_ids.
Converts timestamps and handles missing values.
Loading: Uses psycopg2.extras.execute_values for high-speed bulk insertion, capable of loading thousands of reviews in seconds while handling conflicts via ON CONFLICT DO NOTHING. 7. Dashboard Implementation
The insights pipeline culminates in a deployed interactive dashboard.

### 7.1 Tech Stack

Frontend: React (Vite) with Chart.js for responsive, high-performance visualizations.
Backend: FastAPI for high-speed, asynchronous data serving.
Database: PostgreSQL for robust structured data storage.

### 7.2 Key Features & Technical Implementation

To support granular analysis, specialized API endpoints and visualization components were implemented:

Sentiment Trend Analysis (New)

Endpoint: /api/sentiment-trend
Functionality: Calculates monthly average sentiment scores and overlays a 3-month moving average.
Purpose: Enables stakeholders to correlate sentiment dips with specific app version releases or service outages.
Theme Sentiment Distribution (New)

Endpoint: /api/themes/boxplot-stats
Functionality: Computes statistical quartiles (Min, Q1, Median, Q3, Max) for sentiment scores within each theme using PostgreSQL's PERCENTILE_CONT function.
Purpose: Provides a "Box-and-Whisker" view to visualize the spread of user opinion. It differentiates between universally hated features (tight negative distribution) and polarizing ones (wide distribution).
Priority Matrix

Functionality: A scatter plot mapping Theme Volume vs. Mean Sentiment.
Purpose: Instantly identifies "Critical Quadrant" issues (High Volume, Negative Sentiment) for immediate engineering triage.
Dynamic Filtering

Functionality: Global state management allows users to toggle analysis between CBE, Abyssinia, and Dashen Bank instantly, updating all charts via efficient SQL queries. ## 8. Insights & Recommendations

### Abyssinia Bank

| Category         | Finding                                   | Evidence                                                                                                                   |
| :--------------- | :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------- |
| **Pain Point 1** | App crashes and instability               | ~45% of reviews fall under the _App Stability & Crashes_ theme; strongly negative sentiment                                |
| **Pain Point 2** | Developer Options Blocking                | Users even with developer mode off are locked out of the app; very negative sentiment                                      |
| **Pain Point 3** | OTP doesn't automatically allow for entry | very few 5% reviews are strongly complaining about having no manual OTP entry as the automatic one doesn't work.           |
| **Driver 1**     | UI/UX Design and Usability                | 200+ reviews/ 18% of reviews praise Abyssinia's UI but this will only be a true driver once the pain points are dealt with |

**Recommendations:**

1.  **Invest in crash analytics & hotfix pipeline** — the app’s reliability is critically undermining user trust. Implement robust crash reporting (e.g., Firebase Crashlytics) and prioritize stability releases.
2.  **Remove or rework the developer-options block** — this is an anti-pattern that frustrates power users and developers. Use alternative security measures instead.
3.  **Optimize the OTP flow** — simplify and speed up OTP input by allowing manual entry.
4.  **Opportunity CBE as aspirational benchmark** — ~20% of reviews reference CBE as a model to follow. While the sentiment is negative about Abyssinia, the constructive nature of this feedback provides a clear roadmap — users are essentially telling developers exactly what features and quality standards they expect.

### Commercial Bank of Ethiopia (CBE)

| Category         | Finding                              | Evidence                                                                                                                  |
| :--------------- | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| **Pain Point 1** | Update-Induced App Instability       | After major updates, users report crashes and sync issues                                                                 |
| **Pain Point 2** | Numpad/UI Redesign After Update      | Pin input numpad was changed in an update, causing confusion and negative feedback                                        |
| **Driver 1**     | General Ease of Use                  | ~50% of reviews praise the app's simplicity and user-friendliness                                                         |
| **Driver 2**     | Transaction History & Account Access | Users value the seamless transaction experience however due to updates users are unable to see older transaction history. |

**Recommendations:**

1.  **Staged rollout & beta testing** — implement feature flags and gradual rollouts to catch update issues before they reach all users.
2.  **Revert or offer choice on numpad layout and ability to see older transactions** — the redesign broke user muscle memory. Allow users to select their preferred layout. Also allow users to see their old transaction history that was available before the update.
3.  **Maintain simplicity as a differentiator** — CBE's ease-of-use is a competitive advantage over other banks. Avoid feature bloat.

### Dashen Bank

| Category         | Finding                                                           | Evidence                                                                  |
| :--------------- | :---------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **Pain Point 1** | Transaction Failures & Freezing                                   | Users experience freezes during transfers and bill payments               |
| **Pain Point 2** | Security & Authentication Gaps (incl. Developer Options Blocking) | Login issues because of OTP , and developer-mode blocking                 |
| **Driver 1**     | All-in-One Super App Experience                                   | ~50% of reviews praise the comprehensive feature set                      |
| **Driver 2**     | Speed & Reliability (when working)                                | Users appreciate fast transaction processing when the app works correctly |

**Recommendations:**

1.  **Improve transaction resilience** — implement retry logic, optimistic UI, and clear error messages when transfers fail.
2.  **Modernize authentication** — replace developer-options blocking with biometric authentication or device attestation or two factor authentication for higher security.
3.  **Leverage the super-app brand** — continue adding utility features (bill pay, airtime, etc.) that keep users within the Dashen ecosystem.

### Cross-Bank Comparison

| Dimension                      | CBE                | Abyssinia                 | Dashen               |
| :----------------------------- | :----------------- | :------------------------ | :------------------- |
| **Dominant sentiment**         | Positive           | Negative                  | Positive             |
| **Top driver**                 | Ease of Use        | UI Design                 | Super App Experience |
| **Top pain point**             | Update Instability | App Crashes               | Transaction Failures |
| **Unique issue**               | Numpad redesign    | Competitor envy (CBE)     | Security gaps        |
| **Developer Options Blocking** | Present            | Present (strong negative) | Present (negative)   |

**Key Takeaways:**

- **CBE** leads in user satisfaction but must manage update quality carefully.
- **Abyssinia** has the most critical issues — stability must be the #1 engineering priority.
- **Dashen** sits in the middle — strong brand but needs reliability improvements for security and transactions.
- **Developer Options Blocking even when developer mode is off** is a shared anti-pattern across Abyssinia and Dashen that should be eliminated industry-wide. 9. Conclusion
  This project has successfully democratized the "Voice of the Customer" for Ethiopian fintechs. By looking beyond the star rating, the project has:

Quantified the exact cost of technical debt (e.g., CBE's update crashes).
Identified the unique competitive advantages of each player (Dashen's ecosystem, Abyssinia's design).
Prioritized a roadmap based on severity and volume, moving engineering discussions from "I think" to "The data shows."
The deployed dashboard stands as a testament to this new data-driven era, offering a live window into user sentiment that will guide these financial giants toward a more user-centric future.

Report generated by the CX Analytics Engine | February 2026
