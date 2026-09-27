SELECT 
    COUNT(*) AS total_titles,
    SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) AS movie_count,
    ROUND(100.0 * SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) / COUNT(*), 2) AS movie_pct,
    SUM(CASE WHEN type = 'Tv Show' THEN 1 ELSE 0 END) AS tv_show_count,
    ROUND(100.0 * SUM(CASE WHEN type = 'Tv Show' THEN 1 ELSE 0 END) / COUNT(*), 2) AS tv_show_pct,
    ROUND(AVG(rating_score), 2) AS overall_avg_rating,
    ROUND(AVG(popularity), 2) AS overall_avg_popularity
FROM ott_titles;

SELECT 
    genre, 
    COUNT(*) AS titles,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ott_titles), 2) AS catalog_share_pct
FROM ott_titles 
WHERE genre IS NOT NULL 
GROUP BY genre 
ORDER BY titles DESC 
LIMIT 1;

SELECT 
    release_year, 
    type, 
    COUNT(*) AS titles 
FROM ott_titles 
GROUP BY release_year, type 
ORDER BY release_year ASC, type ASC;

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

SELECT 
    genre, 
    COUNT(*) AS titles 
FROM ott_titles 
WHERE genre IS NOT NULL 
GROUP BY genre 
ORDER BY titles DESC 
LIMIT 10;

SELECT 
    type, 
    ROUND(AVG(popularity), 2) AS avg_popularity 
FROM ott_titles 
WHERE popularity IS NOT NULL 
GROUP BY type;

SELECT 
    rating AS maturity_rating,
    COUNT(*) AS title_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ott_titles), 2) AS pct_of_catalog,
    ROUND(AVG(rating_score), 2) AS avg_rating,
    ROUND(AVG(popularity), 2) AS avg_popularity
FROM ott_titles
GROUP BY rating
ORDER BY title_count DESC;

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
