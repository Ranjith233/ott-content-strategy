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
    
    df = pd.read_csv(raw_path)

    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    df['title'] = df['title'].astype(str).str.strip()
    df['type'] = df['type'].astype(str).str.strip().str.title()
    
    df = df.drop_duplicates(subset=['title', 'type']).reset_index(drop=True)

    min_mask = df['rating'].astype(str).str.contains('min', na=False)
    if min_mask.sum() > 0:
        for idx in df[min_mask].index:
            df.loc[idx, 'duration'] = df.loc[idx, 'rating']
            df.loc[idx, 'rating'] = 'NR'

    def parse_runtime(row):
        dur = str(row.get('duration', ''))
        if 'min' in dur:
            m = re.search(r'(\d+)', dur)
            return int(m.group(1)) if m else np.nan
        elif 'Season' in dur:
            m = re.search(r'(\d+)', dur)
            if m:
                return int(m.group(1)) * 400
        return np.nan

    df['runtime'] = df.apply(parse_runtime, axis=1)

    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    df = df[(df['release_year'] >= 1920) & (df['release_year'] <= 2026)].reset_index(drop=True)
    df['release_year'] = df['release_year'].astype(int)

    valid_ratings = ['TV-MA', 'TV-14', 'TV-PG', 'R', 'PG-13', 'TV-Y7', 'TV-Y', 'PG', 'TV-G', 'NR', 'G', 'NC-17', 'UR']
    df['rating'] = df['rating'].fillna('NR')
    df['rating'] = df['rating'].apply(lambda x: x if x in valid_ratings else 'NR')

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

    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
    df['rating_score'] = pd.to_numeric(df['rating_score'], errors='coerce')

    r_med = round(df['rating_score'].median(), 2)
    p_med = round(df['popularity'].median(), 2)

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

    cols = [
        'title_id', 'title', 'type', 'release_year', 'genre',
        'language', 'country', 'rating', 'runtime', 'popularity',
        'rating_score', 'content_segment', 'is_niche', 'is_recent_release'
    ]
    df_clean = df[cols].copy()

    df_clean.to_csv(proc_csv, index=False)

    if os.path.exists(duckdb_path):
        os.remove(duckdb_path)
    con_duck = duckdb.connect(duckdb_path)
    con_duck.execute("CREATE TABLE ott_titles AS SELECT * FROM df_clean")
    con_duck.close()

    con_sqlite = sqlite3.connect(sqlite_path)
    df_clean.to_sql("ott_titles", con_sqlite, if_exists="replace", index=False)
    con_sqlite.close()

    return df_clean

if __name__ == '__main__':
    run_cleaning()
