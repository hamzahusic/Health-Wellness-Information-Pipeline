import pandas as pd
import numpy as np
import logging
from pathlib import Path
from pymongo import MongoClient
from typing import Optional

logger = logging.getLogger(__name__)

MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME   = 'articles_pipeline'
COLLECTION = 'raw_articles'


def load_from_mongodb(uri: str = MONGO_URI, db: str = DB_NAME, collection: str = COLLECTION, limit: int = 0) -> pd.DataFrame:
    logger.info('Connecting to MongoDB: %s / %s', db, collection)
    client = MongoClient(uri)
    try:
        coll = client[db][collection]
        cursor = coll.find({}, {'_id': 0})
        if limit:
            cursor = cursor.limit(limit)
        df = pd.DataFrame(list(cursor))
        logger.info('Loaded %d rows from MongoDB', len(df))
        return df
    finally:
        client.close()


def save_to_csv(df: pd.DataFrame, path: str) -> None:
    """Export a DataFrame to CSV and log the action."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding='utf-8')
    logger.info('Saved %d rows → %s', len(df), path)


def load_from_csv(path: str, dtype: Optional[dict] = None, parse_dates: Optional[list] = None) -> pd.DataFrame:
    logger.info('Loading CSV: %s', path)
    df = pd.read_csv(
        path,
        dtype=dtype or {'source_id': 'str', 'source_name': 'str', 'author': 'str'},
        parse_dates=parse_dates or ['publishedAt'],
        na_values=['', 'None', 'null', 'N/A'],
        encoding='utf-8',
    )
    logger.info('CSV loaded: shape=%s', df.shape)
    return df

def chunked_stats(path: str, chunk_size: int = 200) -> dict:
    """
    Compute per-source and per-author article counts, plus mean content length,
    by iterating the CSV in chunks — memory-safe for large files.
    """
    logger.info('Chunked stats: path=%s chunk_size=%d', path, chunk_size)

    source_accum = {}
    author_accum = {}
    content_lengths = []
    total_rows = 0

    for chunk in pd.read_csv(
        path,
        chunksize=chunk_size,
        na_values=['', 'None', 'null', 'N/A']
    ):
        total_rows += len(chunk)

        for required in ('source_name', 'author', 'content'):
            if required not in chunk.columns:
                raise ValueError(f"Missing required column: {required}. Columns: {list(chunk.columns)}")

        for source, count in chunk['source_name'].dropna().value_counts().items():
            source_accum[source] = source_accum.get(source, 0) + count

        for author, count in chunk['author'].dropna().value_counts().items():
            author_accum[author] = author_accum.get(author, 0) + count

        lengths = chunk['content'].dropna().str.len()
        content_lengths.append((lengths.sum(), lengths.count()))

    if total_rows == 0:
        raise ValueError("No valid chunks found while processing CSV.")

    total_content_chars = sum(s for s, _ in content_lengths)
    total_content_count = sum(c for _, c in content_lengths)
    mean_content_length = total_content_chars / total_content_count if total_content_count else 0.0

    source_df = (
        pd.DataFrame(list(source_accum.items()), columns=['source_name', 'article_count'])
        .sort_values('article_count', ascending=False)
        .reset_index(drop=True)
    )

    author_df = (
        pd.DataFrame(list(author_accum.items()), columns=['author', 'article_count'])
        .sort_values('article_count', ascending=False)
        .reset_index(drop=True)
    )

    logger.info('Chunked stats complete: total_rows=%d mean_content_length=%.1f', total_rows, mean_content_length)
    return {
        'total_rows': total_rows,
        'mean_content_length': float(mean_content_length),
        'source_df': source_df,
        'author_df': author_df,
    }

def optimise_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df_opt = df.copy()

    if 'publishedAt' in df_opt.columns:
        df_opt['publishedAt'] = pd.to_datetime(df_opt['publishedAt'], errors='coerce', utc=True)
        logger.debug('Parsed publishedAt as datetime')

    for col in ['source_name', 'author']:
        if col in df_opt.columns:
            cardinality = df_opt[col].nunique() / len(df_opt)
            if cardinality < 0.50:
                df_opt[col] = df_opt[col].astype('category')
                logger.debug('Converted to category: %s (cardinality=%.1f%%)', col, cardinality * 100)

    return df_opt


def memory_comparison(df_before: pd.DataFrame, df_after: pd.DataFrame) -> dict:
    before_mb = df_before.memory_usage(deep=True).sum() / 1024**2
    after_mb  = df_after.memory_usage(deep=True).sum()  / 1024**2
    pct       = (1 - after_mb / before_mb) * 100 if before_mb else 0
    logger.info('Memory: %.2f MB → %.2f MB (reduction %.1f%%)', before_mb, after_mb, pct)
    return {'before_mb': before_mb, 'after_mb': after_mb, 'reduction_pct': pct}