# 📊 Power BI & Tableau Implementation Guide
## OTT Content Strategy & Audience Insights

This guide provides step-by-step instructions, DAX measures, and Tableau calculated fields to replicate the 6-page OTT Content Intelligence Dashboard in **Power BI Desktop** or **Tableau Desktop / Public**.

---

## 1. Connecting to the Processed Data
1. Open **Power BI Desktop** or **Tableau Desktop**.
2. Select **Get Data** -> **Text/CSV**.
3. Browse to: `data/processed/ott_titles.csv`.
4. Ensure data types are set as follows:
   - `title_id`: Text
   - `title`: Text
   - `type`: Text
   - `release_year`: Whole Number (Year)
   - `genre`: Text
   - `language`: Text
   - `country`: Text
   - `rating`: Text
   - `runtime`: Decimal / Whole Number
   - `popularity`: Decimal Number
   - `rating_score`: Decimal Number
   - `content_segment`: Text
   - `is_niche`: Whole Number (0/1)
   - `is_recent_release`: Whole Number (0/1)

---

## 2. Power BI DAX Measures & Data Model

Create a dedicated **Measures Table** (`_Measures`) and add the following DAX calculations:

### Key Metrics:
```dax
// Total Titles Count
Total Titles = COUNTROWS(ott_titles)

// Movies Count & Mix %
Movie Count = CALCULATE(COUNTROWS(ott_titles), ott_titles[type] = "Movie")
Movie Share Pct = DIVIDE([Movie Count], [Total Titles], 0)

// TV Shows Count & Mix %
TV Show Count = CALCULATE(COUNTROWS(ott_titles), ott_titles[type] = "Tv Show")
TV Show Share Pct = DIVIDE([TV Show Count], [Total Titles], 0)

// Average Rating (Ignoring Missing)
Avg Rating Score = AVERAGE(ott_titles[rating_score])

// Average Popularity Score
Avg Popularity = AVERAGE(ott_titles[popularity])

// Median Benchmarks for Dynamic Quadrant Segmentation
Median Rating Benchmark = MEDIAN(ott_titles[rating_score])
Median Popularity Benchmark = MEDIAN(ott_titles[popularity])

// Dynamic Segment Classification DAX
Strategic Content Segment = 
VAR R = SELECTEDVALUE(ott_titles[rating_score])
VAR P = SELECTEDVALUE(ott_titles[popularity])
VAR MedR = 6.80
VAR MedP = 43.50
RETURN
    IF(ISBLANK(R) || ISBLANK(P), "Unsegmented (Missing Metric)",
        IF(R >= MedR && P >= MedP, "High Rating + High Pop (Blockbusters)",
            IF(R >= MedR && P < MedP, "High Rating + Low Pop (Hidden Gems)",
                IF(R < MedR && P >= MedP, "Low Rating + High Pop (Guilty Pleasures)",
                    "Low Rating + Low Pop (Underperformers)"
                )
            )
        )
    )
```

---

## 3. Tableau Calculated Fields

In Tableau, open **Analysis** -> **Create Calculated Field**:

1. **Movie Flag**:
   ```tableau
   IF [type] = 'Movie' THEN 1 ELSE 0 END
   ```

2. **TV Show Flag**:
   ```tableau
   IF [type] = 'Tv Show' THEN 1 ELSE 0 END
   ```

3. **Strategic Segment**:
   ```tableau
   IF ISNULL([rating_score]) OR ISNULL([popularity]) THEN "Unsegmented"
   ELSEIF [rating_score] >= 6.8 AND [popularity] >= 43.5 THEN "Blockbusters (High Rating + High Pop)"
   ELSEIF [rating_score] >= 6.8 AND [popularity] < 43.5 THEN "Hidden Gems (High Rating + Low Pop)"
   ELSEIF [rating_score] < 6.8 AND [popularity] >= 43.5 THEN "Guilty Pleasures (Low Rating + High Pop)"
   ELSE "Underperformers (Low Rating + Low Pop)"
   END
   ```

---

## 4. 6-Page Dashboard Layout Blueprint

### Page 1 — Executive Overview
- **Header:** Title, OTT Logo, Subtitle.
- **Top Row KPI Cards:** `Total Titles`, `Movie Share %`, `TV Show Share %`, `Avg Rating Score`, `Avg Popularity`.
- **Center Left:** Donut chart of `type` with % labels.
- **Center Right:** Horizontal Bar Chart of `genre` ordered descending (Top 10).
- **Slicers/Filters:** Release Year Range, Content Type, Segment.

### Page 2 — Content Trends
- **Top Chart:** Stacked Bar Chart of `release_year` (X-axis) vs `titles` (Y-axis), colored by `type`.
- **Bottom Left:** Area Chart of Cumulative Titles over time.
- **Bottom Right:** Multi-line chart of Top 5 genres across release years.

### Page 3 — Language & Market
- **Left:** Horizontal Bar Chart of `country` (Top 15 markets).
- **Right Top:** Bar chart of `language` distribution.
- **Right Bottom:** Scatter plot of `avg_pop` vs `avg_rating` by country (Bubble size = `Total Titles`).

### Page 4 — Ratings & Popularity
- **Left:** Histogram of `rating_score` with reference lines for mean and median.
- **Right Top:** Column chart of content maturity ratings (`TV-MA`, `TV-14`, `R`, `PG-13`, `PG`).
- **Bottom:** Scatter plot of `popularity` (X) vs `rating_score` (Y), color coded by `type`.

### Page 5 — Content Segments (2x2 Matrix)
- **Top Scorecards:** 4 KPI Cards for the 4 Quadrants: Blockbusters, Hidden Gems, Guilty Pleasures, Underperformers.
- **Main Visual:** 2x2 Scatter Plot with Quadrant reference lines (`Rating = 6.8`, `Popularity = 43.5`).
- **Bottom Table:** Hidden Gems Priority Table (Titles with `rating_score >= 8.0` and `popularity < 40`).

### Page 6 — Title Explorer
- **Searchable Grid:** Columns: `title`, `type`, `release_year`, `genre`, `country`, `rating`, `runtime`, `popularity`, `rating_score`, `content_segment`.
- **Interactive Slicers:** Search box, Genre drop-down, Rating slider, Popularity slider.
