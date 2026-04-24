"""
src/analytics/explorer.py
Exploratory data analysis functions for the articles pipeline.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')   # headless — no display server required
import matplotlib.pyplot as plt
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def inspect_shape(df: pd.DataFrame) -> dict:
    """Return shape, column names, and total cell count."""
    info = {
        'rows':    df.shape[0],
        'columns': df.shape[1],
        'cells':   df.size,
        'column_names': df.columns.tolist(),
    }
    logger.info('Shape: %d rows × %d columns', info['rows'], info['columns'])
    return info


def print_info(df: pd.DataFrame) -> None:
    """Call df.info() — shows dtypes and non-null counts."""
    df.info(memory_usage='deep')


def describe_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Return df.describe() for all numeric columns, including content_length if content is present."""
    df = df.copy()
    if 'content' in df.columns:
        df['content_length'] = df['content'].dropna().str.len()
    return df.describe()


def value_counts_report(df: pd.DataFrame,
                        cols: list = None,
                        top_n: int = 15) -> dict:
    """
    Return value_counts and nunique for each column in cols.
    Defaults to ['source_name', 'author'] to match the articles schema.
    """
    if cols is None:
        cols = [c for c in ['source_name', 'author'] if c in df.columns]

    report = {}
    for col in cols:
        counts   = df[col].value_counts().head(top_n)
        n_unique = df[col].nunique()
        report[col] = {'counts': counts, 'nunique': n_unique}
        logger.info('%s: %d unique values', col, n_unique)
    return report


def extract_publish_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse publishedAt and add a publish_year integer column.
    Operates on a copy — original is not modified.
    """
    df = df.copy()
    if 'publishedAt' in df.columns:
        df['publish_year'] = pd.to_datetime(
            df['publishedAt'], errors='coerce', utc=True).dt.year
        logger.info('Extracted publish_year: %d non-null',
                    df['publish_year'].notna().sum())
    return df


def plot_distributions(df: pd.DataFrame, output_path: str) -> None:
    """
    Save a 2×2 chart of article distributions to output_path.
    Uses Agg backend so no display is required.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Article Distributions', fontsize=14, fontweight='bold')

    if 'content' in df.columns:
        content_lengths = df['content'].dropna().str.len()
        content_lengths.plot(
            kind='hist', bins=30, ax=axes[0, 0],
            color='steelblue', edgecolor='white')
        axes[0, 0].set_title('Content Length Distribution')
        axes[0, 0].set_xlabel('Characters')

    if 'source_name' in df.columns:
        top_sources = df['source_name'].value_counts().head(10)
        top_sources.plot(kind='bar', ax=axes[0, 1], color='teal', edgecolor='white')
        axes[0, 1].set_title('Top 10 Sources')
        axes[0, 1].tick_params(axis='x', rotation=45)

    if 'author' in df.columns:
        top_authors = df['author'].value_counts().head(10)
        top_authors.plot(kind='bar', ax=axes[1, 0], color='coral', edgecolor='white')
        axes[1, 0].set_title('Top 10 Authors')
        axes[1, 0].tick_params(axis='x', rotation=45)

    if 'publishedAt' in df.columns:
        df = extract_publish_year(df)

    if 'publish_year' in df.columns:
        year_counts = df['publish_year'].dropna().value_counts().sort_index()
        year_counts.plot(kind='line', ax=axes[1, 1], color='purple', linewidth=2)
        axes[1, 1].set_title('Articles per Publish Year')
        axes[1, 1].set_xlabel('Year')

    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()
    logger.info('Saved distribution chart → %s', output_path)
