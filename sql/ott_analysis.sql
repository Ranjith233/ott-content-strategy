-- =====================================================================
-- OTT Content Strategy & Audience Insights — Analytical Queries
-- Author: Ranjith Kumar
-- Dialect: PostgreSQL / DuckDB / SQLite (3.25+)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. EXECUTIVE KPI BASELINE
-- ---------------------------------------------------------------------

-- Overall catalog volume, format split (Movies vs TV Series), and mean scores
SELECT 
    COUNT(*) AS total_titles,
    SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) AS movie_count,
    ROUND(100.0 * SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) / COUNT(*), 2) AS movie_pct,
    SUM(CASE WHEN type = 'Tv Show' THEN 1 ELSE 0 END) AS tv_show_count,
    ROUND(100.0 * SUM(CASE WHEN type = 'Tv Show' THEN 1 ELSE 0 END) / COUNT(*), 2) AS tv_show_pct,
    ROUND(AVG(rating_score), 2) AS overall_avg_rating,
    ROUND(AVG(popularity), 2) AS overall_avg_popularity
FROM ott_titles;

-- Identify the single top genre anchoring the catalog
SELECT 
    genre, 
    COUNT(*) AS titles,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ott_titles), 2) AS catalog_share_pct
FROM ott_titles 
WHERE genre IS NOT NULL 
GROUP BY genre 
ORDER BY titles DESC 
LIMIT 1;

-- ---------------------------------------------------------------------
-- 2. CONTENT TRENDS & FORMAT SHIFTS OVER TIME
-- ---------------------------------------------------------------------

-- Business Question: How has the catalog changed over time?
-- Annual release counts grouped by content format
SELECT 
    release_year, 
    type, 
    COUNT(*) AS titles 
FROM ott_titles 
GROUP BY release_year, type 
ORDER BY release_year ASC, type ASC;

-- Year-over-Year (YoY) content growth and cumulative catalog trajectory
-- Using LAG() to see how the expansion accelerated after 2015
WITH annual_summary AS (
    SELECT 
        release_year,
        COUNT(*) AS total_annual_titles,
        SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) AS movie_titles,
        SUM(CASE WHEN type = 'Tv Show' THEN 1 ELSE 0 END) AS tv_titles
    FROM ott_titles
    WHERE release_year >= 2000
    GROUP BY release_year
)
SELECT 
    release_year,
    total_annual_titles,
    movie_titles,
    tv_titles,
    ROUND(100.0 * tv_titles / NULLIF(total_annual_titles, 0), 2) AS tv_share_pct,
    LAG(total_annual_titles, 1) OVER (ORDER BY release_year) AS prev_year_titles,
    ROUND(100.0 * (total_annual_titles - LAG(total_annual_titles, 1) OVER (ORDER BY release_year)) 
        / NULLIF(LAG(total_annual_titles, 1) OVER (ORDER BY release_year), 0), 2) AS yoy_growth_pct,
    SUM(total_annual_titles) OVER (ORDER BY release_year ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_titles
FROM annual_summary
ORDER BY release_year ASC;

-- Track how dominant genres evolved across release eras
SELECT 
    genre,
    SUM(CASE WHEN release_year < 2010 THEN 1 ELSE 0 END) AS era_pre_2010,
    SUM(CASE WHEN release_year BETWEEN 2010 AND 2017 THEN 1 ELSE 0 END) AS era_2010_2017,
    SUM(CASE WHEN release_year >= 2018 THEN 1 ELSE 0 END) AS era_2018_present,
    COUNT(*) AS total_titles
FROM ott_titles
GROUP BY genre
ORDER BY total_titles DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- 3. LANGUAGE & GLOBAL MARKET ANALYSIS
-- ---------------------------------------------------------------------

-- Business Question: Which countries or markets contribute the most titles?
-- Top 15 producing countries ranked by volume, average rating, and popularity
SELECT 
    country,
    COUNT(*) AS title_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ott_titles), 2) AS market_share_pct,
    ROUND(AVG(rating_score), 2) AS avg_rating_score,
    ROUND(AVG(popularity), 2) AS avg_popularity
FROM ott_titles
WHERE country IS NOT NULL AND country != 'Unknown'
GROUP BY country
ORDER BY title_count DESC
LIMIT 15;

-- Top languages by title count and average viewer reception
SELECT 
    language,
    COUNT(*) AS title_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ott_titles), 2) AS language_share_pct,
    ROUND(AVG(rating_score), 2) AS avg_rating,
    ROUND(AVG(popularity), 2) AS avg_popularity
FROM ott_titles
GROUP BY language
ORDER BY title_count DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- 4. RATINGS & POPULARITY DYNAMICS
-- ---------------------------------------------------------------------

-- Top 10 genres by title volume
SELECT 
    genre, 
    COUNT(*) AS titles 
FROM ott_titles 
WHERE genre IS NOT NULL 
GROUP BY genre 
ORDER BY titles DESC 
LIMIT 10;

-- Average popularity by content format (Movies vs Series)
SELECT 
    type, 
    ROUND(AVG(popularity), 2) AS avg_popularity 
FROM ott_titles 
WHERE popularity IS NOT NULL 
GROUP BY type;

-- Maturity rating distribution across the catalog
SELECT 
    rating AS maturity_rating,
    COUNT(*) AS title_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ott_titles), 2) AS pct_of_catalog,
    ROUND(AVG(rating_score), 2) AS avg_rating,
    ROUND(AVG(popularity), 2) AS avg_popularity
FROM ott_titles
GROUP BY rating
ORDER BY title_count DESC;

-- Genre performance comparison (Volume, Rating, and Popularity)
SELECT 
    genre,
    COUNT(*) AS titles,
    ROUND(AVG(rating_score), 2) AS avg_rating,
    ROUND(AVG(popularity), 2) AS avg_popularity,
    ROUND(AVG(runtime), 1) AS avg_runtime_mins
FROM ott_titles
GROUP BY genre
HAVING COUNT(*) >= 50
ORDER BY avg_popularity DESC;

-- ---------------------------------------------------------------------
-- 5. 2x2 STRATEGIC CONTENT SEGMENTATION
-- ---------------------------------------------------------------------

-- Content segment breakdown with average rating, popularity, and format mix
SELECT 
    content_segment,
    COUNT(*) AS title_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ott_titles), 2) AS segment_pct,
    ROUND(AVG(rating_score), 2) AS avg_rating,
    ROUND(AVG(popularity), 2) AS avg_popularity,
    SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) AS movie_count,
    SUM(CASE WHEN type = 'Tv Show' THEN 1 ELSE 0 END) AS tv_show_count
FROM ott_titles
GROUP BY content_segment
ORDER BY title_count DESC;

-- Strategic Action: Top Hidden Gems (Rating >= 8.0, Low Popularity)
-- High-priority candidates for recommendation carousels and marketing promotion
SELECT 
    title,
    type,
    release_year,
    genre,
    language,
    country,
    rating_score,
    popularity
FROM ott_titles
WHERE content_segment LIKE '%Hidden Gems%'
  AND rating_score >= 8.0
ORDER BY rating_score DESC, popularity ASC
LIMIT 15;

-- Strategic Action: Catalog Bloat Review (Rating <= 4.5, Popularity <= 25.0)
-- Prime candidates for contract non-renewal / de-licensing
SELECT 
    title,
    type,
    release_year,
    genre,
    language,
    rating_score,
    popularity
FROM ott_titles
WHERE content_segment LIKE '%Underperformers%'
  AND rating_score <= 4.5
  AND popularity <= 25.0
ORDER BY rating_score ASC, popularity ASC
LIMIT 15;

-- ---------------------------------------------------------------------
-- 6. DATA VALIDATION & RECONCILIATION CHECKS
-- ---------------------------------------------------------------------

-- Cross-checking total rows, non-null IDs, missing values, and min/max ranges
SELECT 
    COUNT(*) AS total_rows,
    COUNT(title_id) AS non_null_ids,
    COUNT(DISTINCT title_id) AS unique_ids,
    SUM(CASE WHEN rating_score IS NULL THEN 1 ELSE 0 END) AS missing_ratings,
    SUM(CASE WHEN popularity IS NULL THEN 1 ELSE 0 END) AS missing_popularity,
    MIN(release_year) AS min_year,
    MAX(release_year) AS max_year,
    MIN(rating_score) AS min_rating,
    MAX(rating_score) AS max_rating,
    MIN(popularity) AS min_pop,
    MAX(popularity) AS max_pop
FROM ott_titles;
