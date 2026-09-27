"""
Data Pipeline entry point (delegates to clean_data.py).
Author: Ranjith Kumar
"""
from src.clean_data import run_cleaning

if __name__ == '__main__':
    run_cleaning()
