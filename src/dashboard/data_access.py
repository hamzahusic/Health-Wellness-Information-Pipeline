"""
MongoDB data access helpers for the Health & Wellness dashboard.
All query logic lives here; callbacks import these functions.

Column mapping for this project's cleaned CSV:
  published_year  → publication year
  Word Count      → article word count
  Category        → health/wellness category
  source_name     → news source name
  title           → article title
  author          → article author
  content         → full article text
"""
import os
import pandas as pd
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "articles_pipeline")

_client = None

COL_YEAR = "published_year"
COL_WORD_COUNT = "Word Count"
COL_CATEGORY = "Category"
COL_SOURCE = "source_name"
COL_TITLE = "title"
COL_AUTHOR = "author"
COL_CONTENT = "content"


def get_client() -> MongoClient:
    """Return a shared MongoClient (lazy singleton)."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_collection(name: str):
    return get_client()[DB_NAME][name]


def load_articles_df() -> pd.DataFrame:
    """
    Load all articles from MongoDB into a DataFrame.
    Falls back to the cleaned CSV if MongoDB is unavailable or if the
    collection contains raw pipeline docs instead of cleaned article data.
    """
    try:
        col = get_collection("raw_articles")
        docs = list(col.find({}, {"_id": 0}))
        if docs:
            df = pd.DataFrame(docs)
            # Only use MongoDB data if it has the cleaned article schema.
            # The raw_articles collection may contain storage-wrapper docs
            # (fields: data, source, fetched_at, version) instead.
            if COL_SOURCE in df.columns and COL_TITLE in df.columns:
                return df
    except Exception:
        pass

    base = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
    for rel in ("cleaned/articles_clean.csv", "cleaned/articles_cleaned.csv"):
        path = os.path.join(base, rel)
        if os.path.exists(path):
            return pd.read_csv(path)

    return pd.DataFrame()


def get_categories(df: pd.DataFrame) -> list:
    """Return a sorted list of unique health categories for the dropdown."""
    if COL_CATEGORY in df.columns:
        return sorted(df[COL_CATEGORY].dropna().unique().tolist())
    return []


def get_years(df: pd.DataFrame) -> tuple:
    """Return (min_year, max_year) from the dataset."""
    if COL_YEAR in df.columns:
        years = pd.to_numeric(df[COL_YEAR], errors="coerce").dropna()
        if not years.empty:
            return int(years.min()), int(years.max())
    return 2020, 2026


def filter_articles(
    df: pd.DataFrame,
    category=None,
    year_range=None,
    search=None,
) -> pd.DataFrame:
    """
    Apply filters to the articles DataFrame.
    All filters are optional; passing None skips that filter.
    """
    result = df.copy()

    if category and COL_CATEGORY in result.columns:
        result = result[result[COL_CATEGORY] == category]

    if year_range and COL_YEAR in result.columns:
        lo, hi = year_range
        result = result[pd.to_numeric(result[COL_YEAR], errors="coerce").between(lo, hi)]

    if search and search.strip() and COL_TITLE in result.columns:
        mask = result[COL_TITLE].str.contains(search.strip(), case=False, na=False)
        result = result[mask]

    return result
