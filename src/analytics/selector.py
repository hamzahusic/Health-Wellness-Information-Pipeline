"""
src/analytics/selector.py
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def select_columns(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Return a DataFrame with only the columns that exist in df."""
    existing = [c for c in cols if c in df.columns]
    logger.info('Selecting %d/%d columns', len(existing), len(cols))
    return df[existing]


def loc_filter(df: pd.DataFrame,
               min_content_len: int = 200,
               result_cols: list = None) -> pd.DataFrame:
    """
    Use df.loc with a boolean mask to select articles with substantial content.
    Returns only result_cols columns (or a default set).
    """
    if result_cols is None:
        result_cols = ['title', 'source_name', 'author', 'publishedAt']
    result_cols = [c for c in result_cols if c in df.columns]
    mask   = df['content'].str.len().fillna(0) >= min_content_len
    result = df.loc[mask, result_cols]
    logger.info('loc filter (content_len >= %d): %d rows', min_content_len, len(result))
    return result


def iloc_sample(df: pd.DataFrame, step: int = 100) -> pd.DataFrame:
    """
    Use df.iloc with a step to sample every N-th row.
    Useful for quick inspection without random_state dependency.
    """
    result = df.iloc[::step]
    logger.info('iloc sample (step=%d): %d rows', step, len(result))
    return result


def boolean_filter(df: pd.DataFrame,
                   min_content_len: int = 100,
                   require_author: bool = True,
                   require_title: bool = True) -> pd.DataFrame:
    """
    Combined boolean filter: articles with content, optionally requiring
    a non-null author and title.
    """
    mask = df['content'].notna() & (df['content'].str.len() > min_content_len)
    if require_author and 'author' in df.columns:
        mask = mask & df['author'].notna()
    if require_title and 'title' in df.columns:
        mask = mask & df['title'].notna()
    result = df[mask]
    logger.info('boolean_filter: %d rows match', len(result))
    return result


def isin_filter(df: pd.DataFrame,
                sources: list = None,
                exclude: bool = False) -> pd.DataFrame:
    """
    Filter by source_name using isin.
    If exclude=True, returns rows NOT in the sources list.
    """
    if sources is None:
        sources = []
    mask = df['source_name'].isin(sources)
    if exclude:
        mask = ~mask
    result = df[mask]
    logger.info('isin_filter (exclude=%s): %d rows', exclude, len(result))
    return result


def between_filter(df: pd.DataFrame,
                   col: str = 'content',
                   low: float = 200.0,
                   high: float = 2000.0) -> pd.DataFrame:
    """
    Select rows where the length of a string column (e.g. 'content')
    falls between low and high characters (inclusive).
    """
    lengths = df[col].dropna().str.len()
    result = df.loc[lengths.between(low, high).reindex(df.index, fill_value=False)]
    logger.info('between_filter %s [%.0f, %.0f]: %d rows', col, low, high, len(result))
    return result
