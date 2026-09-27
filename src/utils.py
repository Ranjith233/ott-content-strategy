import os
import pandas as pd

def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

def load_catalog(processed=True):
    root = get_project_root()
    if processed:
        file_path = os.path.join(root, "data", "processed", "ott_titles.csv")
    else:
        file_path = os.path.join(root, "data", "raw", "ott_titles_raw.csv")
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Catalog file not found at: {file_path}")
        
    df = pd.read_csv(file_path)
    if 'release_year' in df.columns:
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    return df

def get_benchmarks(df):
    median_rating = round(df['rating_score'].median(), 2)
    median_pop = round(df['popularity'].median(), 2)
    return {
        'rating_median': median_rating,
        'popularity_median': median_pop
    }
