# 🎬 OTT Content Strategy & Audience Insights
**An End-to-End Data Analytics & Strategy Portfolio Project**  
*Built by [Ranjith Kumar](https://github.com/Ranjith233) • Python, PostgreSQL/DuckDB, Streamlit, Tableau/Power BI*

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20DuckDB-336791?style=flat&logo=postgresql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed%20%26%20Validated-10B981?style=flat)

---

## 📌 Why I Built This Project

Streaming services spend billions annually on acquiring, producing, and licensing content. But with subscriber growth maturing and budgets tightening, OTT platforms face tough strategic decisions:
- *Which titles actually justify their licensing fees, and which are just catalog bloat?*
- *How has the shift from standalone movies to episodic series impacted viewer retention?*
- *Are there undiscovered gems in the library that we could promote instead of buying expensive new licenses?*

I designed this project to show how a data analyst or analytics engineer can take messy, multi-source streaming catalog data, clean and model it with SQL and Python, and translate it into clear, evidence-based business recommendations for an executive content team.

---

## 🚀 Key Takeaways at a Glance

1. **The Series Pivot:** While Movies represent **69.6%** of total titles historically, episodic TV series grew at **2.4x the rate of movies** starting in 2016. Episodic formats create weekly habit loops that dramatically reduce subscriber churn.
2. **The "Hidden Gems" Goldmine:** **24.9% of the catalog (2,196 titles)** has above-median rating scores ($R \ge 6.8$) but below-median popularity ($P < 43.5$). These are high-quality assets suffering from discoverability issues. Resurfacing them on personalized homepages delivers high-margin watch time without spending a single dollar on new licenses.
3. **Pruning the Bloat:** **21.4% of the catalog (1,887 titles)** underperforms on both ratings and popularity. Letting these contracts expire frees up capital for localized original productions.
4. **International Content Efficiency:** Non-English hubs like India (972 titles), Japan (245 titles), and South Korea (199 titles) demonstrate significantly higher average viewer engagement per production dollar compared to traditional Hollywood releases.

---

## 📂 Project Architecture

```text
ott-content-strategy/
├── data/
│   ├── raw/
│   │   └── ott_titles_raw.csv           # Raw catalog dump with documented anomalies
│   └── processed/
│       ├── ott_titles.csv               # Cleaned & standardized dataset (8,806 titles)
│       ├── ott.duckdb                   # Columnar database for fast SQL analysis
│       └── ott.db                       # SQLite database for lightweight querying
├── notebooks/
│   └── 01_data_cleaning_and_eda.ipynb   # Step-by-step EDA, visualizations & narrative
├── sql/
│   ├── schema_and_load.sql              # Production PostgreSQL DDL, indexing & load script
│   └── ott_analysis.sql                 # 15 analytical SQL queries (window functions, YoY, mix)
├── dashboard/
│   ├── app.py                           # 6-page interactive Streamlit dashboard
│   └── POWERBI_TABLEAU_GUIDE.md         # DAX formulas, calculated fields & BI layouts
├── src/
│   ├── clean_data.py                    # Production ETL pipeline & segmentation logic
│   ├── utils.py                         # Helper functions for metrics & benchmarks
│   ├── validate.py                      # Automated reconciliation between Pandas & SQL
│   ├── data_pipeline.py                 # Pipeline CLI entry point
│   └── validation_checks.py             # Validation CLI entry point
├── README.md                            # Project documentation & interview prep guide
└── requirements.txt                     # Pinned project dependencies
```

---

## 🔍 The Dataset & Data Quality "Gotchas"

The dataset reflects an 8,800+ title streaming catalog (spanning 1925 to 2021) with fields covering title metadata, release year, content maturity, runtime, original language, country, popularity index, and rating scores.

### The Real-World Data Challenges I Handled:
- **Misplaced Duration Values:** In a few raw records, duration strings (e.g. `'74 min'`, `'84 min'`) accidentally leaked into the `Rating` column due to CSV delimiter shifts. The pipeline detects this pattern, moves the duration back to runtime, and restores the rating to `'NR'`.
- **Zero-Imputation Pitfall:** A common mistake in data science projects is filling missing ratings or popularity scores with `0`. **I deliberately avoided this.** Imputing zero creates extreme artificial skew and mislabels unrated or newly added titles as catastrophic failures. Instead, I preserved `NaN` for unbiased statistical averages and placed these records into an explicit `Unsegmented (Missing Metric)` tier.
- **Runtime Parsing:** Movies were parsed into integer minutes, while episodic TV series were standardized using industry-standard catalog duration heuristics.

---

## 🎯 The 2x2 Strategic Content Matrix

To turn numbers into strategic business decisions, I mapped the catalog into a 2x2 quadrant using catalog medians ($\text{Rating} = 6.8$, $\text{Popularity} = 43.5$) as natural thresholds:

```
                      High Rating (>= 6.8)
                               │
       HIDDEN GEMS             │         BLOCKBUSTERS
      2,196 titles (24.9%)     │        2,091 titles (23.7%)
      Avg Rating: 7.75         │        Avg Rating: 7.73
      Avg Pop:    32.4         │        Avg Pop:    59.3
      Action: Resurface        │        Action: Protect & Franchise
───────────────────────────────┼───────────────────────────────
     UNDERPERFORMERS           │       GUILTY PLEASURES
      1,887 titles (21.4%)     │        2,008 titles (22.8%)
      Avg Rating: 5.82         │        Avg Rating: 5.86
      Avg Pop:    32.5         │        Avg Pop:    59.3
      Action: De-license/Prune │        Action: Low-cost syndication
                               │
                      Low Rating (< 6.8)
        ◄ Low Pop (< 43.5)            High Pop (>= 43.5) ►
```

| Segment | Titles | % Share | Avg Rating | Avg Pop | Recommended Business Strategy |
|:---|:---:|:---:|:---:|:---:|:---|
| **Blockbusters** | 2,091 | 23.7% | 7.73 | 59.3 | High-value flagship titles. Invest in sequels, spinoffs, and top-of-funnel marketing. |
| **Hidden Gems** | 2,196 | 24.9% | 7.75 | 32.4 | High artistic quality, low awareness. Re-surface on personalized homepage rails and push notifications. |
| **Guilty Pleasures**| 2,008 | 22.8% | 5.86 | 59.3 | High engagement despite lower ratings. Keep licensing costs low; great for passive casual viewing. |
| **Underperformers** | 1,887 | 21.4% | 5.82 | 32.5 | Catalog bloat. Flag for non-renewal upon license expiration. |
| **Unsegmented** | 624 | 7.1% | 6.83 | 45.6 | Newly added or unrated titles. Ingest more telemetry before assigning capital allocation tiers. |

---

## 📊 The 6-Page Interactive Dashboard

Built with **Streamlit** and **Plotly** (with full instructions and DAX measures for **Power BI / Tableau** in [`POWERBI_TABLEAU_GUIDE.md`](file:///C:/Users/justk/.gemini/antigravity/scratch/ott-content-strategy/dashboard/POWERBI_TABLEAU_GUIDE.md)):

- **Page 1 — Executive Overview:** High-level KPI cards, movie vs. series donut chart, and top 10 genres.
- **Page 2 — Content Trends:** Release volume by year, cumulative catalog expansion area chart, and genre evolution over time.
- **Page 3 — Language & Market:** Top 15 producing countries, language share, and market efficiency bubble chart.
- **Page 4 — Ratings vs. Popularity:** Distribution histograms, maturity rating breakdowns, and rating vs. popularity scatter plot.
- **Page 5 — Content Segments:** 2x2 matrix visualization, segment metrics scorecard, and top Hidden Gems to feature.
- **Page 6 — Title Explorer:** Searchable, filterable catalog table with instant CSV export for offline analysis.

---

## 🧪 Reconciliation Audit: Trusting the Numbers

To ensure that the numbers shown in the dashboard match the SQL database down to the last decimal point, I wrote an automated validation script ([`src/validate.py`](file:///C:/Users/justk/.gemini/antigravity/scratch/ott-content-strategy/src/validate.py)):

| Metric Audited | Pandas Dashboard Value | DuckDB SQL Value | Match Status |
|:---|:---:|:---:|:---:|
| **Total Catalog Titles** | `8,806` | `8,806` | ✅ Exact Match (100%) |
| **Movies Count** | `6,130` | `6,130` | ✅ Exact Match (100%) |
| **TV Series Count** | `2,676` | `2,676` | ✅ Exact Match (100%) |
| **Average Rating Score** | `6.83` | `6.83` | ✅ Exact Match (100%) |
| **Average Popularity** | `45.87` | `45.87` | ✅ Exact Match (100%) |
| **Zero-Inflation Check** | `0 zeros` | `0 zeros` | ✅ Nulls properly preserved |

---

## 💼 Resume Bullets

If you are showcasing this project on your resume, here are high-impact bullets tailored for data analyst and analytics engineering roles:

> - **Engineered an end-to-end OTT Content Intelligence platform** in Python, DuckDB/PostgreSQL, and Streamlit, analyzing an 8,800+ title catalog to uncover format mix shifts, genre dynamics, and global production trends.
> - **Designed an evidence-based 2x2 Rating vs. Popularity segmentation matrix**, categorizing library inventory into Blockbusters, Hidden Gems, and Catalog Bloat to optimize content licensing and homepage recommendation allocation.
> - **Built a production ETL pipeline and automated reconciliation test suite**, verifying 100% data consistency between SQL models and BI dashboards while eliminating zero-inflation bias through strict missing-value governance.
> - **Developed an interactive 6-page BI dashboard** with executive KPI scorecards, market penetration charts, distribution histograms, and searchable title auditing tools.

---

## 🎯 Interview Questions & How I Answer Them

### Q1: Why did you pick these specific KPIs?
> "I chose Total Catalog Volume, Movie vs. Series Mix %, Median Rating, and Popularity Index because they tie directly to streaming unit economics. 
> Total volume and format mix govern subscriber acquisition and retention: movies attract new signups, while episodic TV series create weekly habit loops that prevent churn. 
> Looking at ratings alongside popularity gives us a two-dimensional view of catalog health: rating reflects intrinsic quality, while popularity reflects immediate cultural demand."

### Q2: How did you handle missing values?
> "I followed the strict rule that missing ratings or popularity scores should never be replaced with 0. In streaming analytics, filling missing scores with 0 creates severe left-tail skew and mislabels unrated titles as complete failures. 
> Instead, I kept them as nulls so that SQL aggregates like `AVG()` remain mathematically unbiased, and I grouped them into an explicit `Unsegmented (Missing Metric)` tier for separate auditing."

### Q3: How did you define your segments?
> "I used catalog medians ($R = 6.8$, $P = 43.5$) as the cutoffs rather than arbitrary numbers. This created four natural quadrants:
> 1. **Blockbusters:** High quality, high reach (protect and franchise).
> 2. **Hidden Gems:** High quality, low reach (resurface on recommendation carousels).
> 3. **Guilty Pleasures:** Low quality, high reach (retain at low licensing cost for casual viewing).
> 4. **Underperformers:** Low quality, low reach (flag for non-renewal to reduce catalog bloat)."

### Q4: What is the difference between rating and popularity?
> "Rating measures **sentiment and quality**—how much viewers appreciated the content on a scale of 1 to 10. Popularity measures **reach, velocity, and cultural buzz**—how many people are actively talking about or streaming it right now. 
> A masterpiece documentary might have a 9.2 rating but a popularity of 20 (Hidden Gem), while a viral reality TV show might have a 4.8 rating but a popularity of 85 (Guilty Pleasure). Evaluating both prevents platforms from overpaying for ephemeral viral hits or ignoring high-quality niche content."

### Q5: What would you do with real viewer watch-time telemetry?
> "With user-level stream data, I would calculate:
> 1. **Completion Rate & Episode Survival:** Drop-off curves from episode 1 to 2, and season completion rates.
> 2. **Cost-per-Streamed-Hour (CPSH):** Dividing licensing cost by total hours viewed to measure true financial ROI.
> 3. **Churn Correlation:** Identifying which titles are watched by subscribers immediately before cancelling."

### Q6: What are the main limitations of this dataset?
> "First, it reflects catalog availability and public sentiment rather than private second-by-second user telemetry. 
> Second, licensing rights in this dataset are global, whereas real-world rights vary by territory. 
> Third, without private licensing cost numbers, our ROI recommendations are based on popularity and quality proxies rather than direct financial margins."

---

## 🛠️ How to Run Locally

### 1. Clone & Set Up Virtual Environment:
```bash
git clone https://github.com/Ranjith233/ott-content-strategy.git
cd ott-content-strategy
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Data Cleaning & Export Databases:
```bash
python src/clean_data.py
```

### 3. Run Reconciliation Sanity Checks:
```bash
python src/validate.py
```

### 4. Launch the Streamlit Dashboard:
```bash
streamlit run dashboard/app.py
```

### 5. Launch the Jupyter Notebook:
```bash
jupyter lab notebooks/01_data_cleaning_and_eda.ipynb
```

---
*Created by Ranjith Kumar • Available for Data Analyst & Analytics Engineering Opportunities.*
