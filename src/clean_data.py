"""
Data Cleaning & Transformation Pipeline
----------------------------------------
Cleans the raw OTT catalog, fixes data anomalies, handles missing values
without zero-imputation bias, creates the 2x2 content segments, and exports
to CSV and DuckDB/SQLite databases.

Author: Ranjith Kumar
"""
import os
import re
import numpy as np
import pandas as pd
import duckdb
import sqlite3

def run_cleaning():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, "data", "raw", "ott_titles_raw.csv")
    proc_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(proc_dir, exist_ok=True)
    
    proc_csv = os.path.join(proc_dir, "ott_titles.csv")
    duckdb_path = os.path.join(proc_dir, "ott.duckdb")
    sqlite_path = os.path.join(proc_dir, "ott.db")
    
    print(f"Loading raw data from: {raw_path}")
    df = pd.read_csv(raw_path)
    print(f"Initial shape: {df.shape}")

    # 1. Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # 2. Strip whitespace and drop duplicate titles
    df['title'] = df['title'].astype(str).str.strip()
    df['type'] = df['type'].astype(str).str.strip().str.title()
    
    initial_len = len(df)
    df = df.drop_duplicates(subset=['title', 'type']).reset_index(drop=True)
    print(f"Dropped {initial_len - len(df)} duplicate records.")

    # 3. Fix misplaced duration values in rating column
    # Notice: In raw streaming data dumps, sometimes duration like '74 min' leaks into rating
    min_mask = df['rating'].astype(str).str.contains('min', na=False)
    if min_mask.sum() > 0:
        print(f"Fixing {min_mask.sum()} records with duration in rating column...")
        for idx in df[min_mask].index:
            df.loc[idx, 'duration'] = df.loc[idx, 'rating']
            df.loc[idx, 'rating'] = 'NR'

    # 4. Extract numeric runtime (minutes)
    def parse_runtime(row):
        dur = str(row.get('duration', ''))
        if 'min' in dur:
            m = re.search(r'(\d+)', dur)
            return int(m.group(1)) if m else np.nan
        elif 'Season' in dur:
            m = re.search(r'(\d+)', dur)
            if m:
                # 1 season is approximately 8-10 episodes * 45 min
                return int(m.group(1)) * 400
        return np.nan

    df['runtime'] = df.apply(parse_runtime, axis=1)

    # 5. Clean release years and ratings
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    # Filter out obvious invalid sentinel years
    df = df[(df['release_year'] >= 1920) & (df['release_year'] <= 2026)].reset_index(drop=True)
    df['release_year'] = df['release_year'].astype(int)

    valid_ratings = ['TV-MA', 'TV-14', 'TV-PG', 'R', 'PG-13', 'TV-Y7', 'TV-Y', 'PG', 'TV-G', 'NR', 'G', 'NC-17', 'UR']
    df['rating'] = df['rating'].fillna('NR')
    df['rating'] = df['rating'].apply(lambda x: x if x in valid_ratings else 'NR')

    # 6. Harmonize genres, countries, and languages
    genre_mapping = {
        'Anime Features': 'Anime',
        'Anime Series': 'Anime',
        'Children & Family Movies': 'Kids & Family',
        'Kids\' TV': 'Kids & Family',
        'Romantic Movies': 'Romance',
        'Romantic TV Shows': 'Romance',
        'International TV Shows': 'International',
        'International Movies': 'International',
        'Crime TV Shows': 'Crime',
        'Horror Movies': 'Horror'
    }
    df['genre'] = df['genre'].replace(genre_mapping).str.strip().fillna('General')
    df['country'] = df['country'].fillna('Unknown').str.strip()
    df['language'] = df['language'].fillna('English').str.strip()

    # 7. Convert quality metrics to numeric
    # IMPORTANT: We do NOT replace missing ratings or popularity with 0!
    # A 0.0 rating skews the true distribution and falsely marks unrated titles as terrible.
    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
    df['rating_score'] = pd.to_numeric(df['rating_score'], errors='coerce')

    # Medians for segmentation cutoffs
    r_med = round(df['rating_score'].median(), 2)
    p_med = round(df['popularity'].median(), 2)
    print(f"Segmentation Benchmarks: Median Rating = {r_med}, Median Popularity = {p_med}")

    # 8. Create 2x2 Strategic Content Segments
    def segment_title(row):
        r = row['rating_score']
        p = row['popularity']
        if pd.isna(r) or pd.isna(p):
            return "Unsegmented (Missing Metric)"
        if r >= r_med and p >= p_med:
            return "High Rating + High Popularity (Blockbusters)"
        elif r >= r_med and p < p_med:
            return "High Rating + Low Popularity (Hidden Gems)"
        elif r < r_med and p >= p_med:
            return "Low Rating + High Popularity (Guilty Pleasures)"
        else:
            return "Low Rating + Low Popularity (Underperformers)"

    df['content_segment'] = df.apply(segment_title, axis=1)
    df['is_niche'] = ((df['language'] != 'English') | (df['genre'].isin(['Anime', 'Documentaries', 'Stand-Up Comedy', 'Horror']))).astype(int)
    df['is_recent_release'] = (df['release_year'] >= 2018).astype(int)

    # Select final clean columns
    cols = [
        'title_id', 'title', 'type', 'release_year', 'genre',
        'language', 'country', 'rating', 'runtime', 'popularity',
        'rating_score', 'content_segment', 'is_niche', 'is_recent_release'
    ]
    df_clean = df[cols].copy()

    # Export to CSV
    df_clean.to_csv(proc_csv, index=False)
    print(f"Exported clean CSV to: {proc_csv} ({len(df_clean)} records)")

    # Export to DuckDB & SQLite for easy querying
    if os.path.exists(duckdb_path):
        os.remove(duckdb_path)
    con_duck = duckdb.connect(duckdb_path)
    con_duck.execute("CREATE TABLE ott_titles AS SELECT * FROM df_clean")
    con_duck.close()

    con_sqlite = sqlite3.connect(sqlite_path)
    df_clean.to_sql("ott_titles", con_sqlite, if_exists="replace", index=False)
    con_sqlite.close()
    print("Databases (DuckDB and SQLite) updated successfully.")

    return df_clean

if __name__ == '__main__':
    run_cleaning()
