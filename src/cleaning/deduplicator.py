import pandas as pd
import logging

logger = logging.getLogger(__name__)

def drop_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(keep='first')
    after = len(df)
    logger.info('drop_exact_duplicates: removed %d rows', before - after)
    return df.reset_index(drop=True)

def drop_duplicate_ids(df: pd.DataFrame, id_col: str = 'url') -> pd.DataFrame:
    actual_col = id_col if id_col in df.columns else None
    if actual_col is None and 'url' in df.columns:
        actual_col = 'url'
    if actual_col is None:
        logger.info('drop_duplicate_ids: no id column found, skipping')
        return df

    before = len(df)
    df = df.drop_duplicates(subset=[actual_col], keep='first')
    after = len(df)
    logger.info('drop_duplicate_ids (%s): removed %d rows', actual_col, before - after)
    return df.reset_index(drop=True)

def drop_duplicate_titles(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    if 'publishedAt' in df.columns:
        subset = ['title', 'publishedAt']
    else:
        subset = ['title']

    df = df.drop_duplicates(subset=subset, keep='first')
    after = len(df)
    logger.info('drop_duplicate_titles: removed %d rows using %s', before - after, subset)
    return df.reset_index(drop=True)

def count_duplicates(df: pd.DataFrame, col: str = 'url') -> int:
    if col not in df.columns:
        return 0
    return int(df.duplicated(subset=[col]).sum())