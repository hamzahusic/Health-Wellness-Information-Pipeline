import pandas as pd
import logging

logger = logging.getLogger(__name__)


def convert_dates(df: pd.DataFrame) -> pd.DataFrame:
    if 'publishedAt' not in df.columns:
        return df
    df['publishedAt'] = pd.to_datetime(
        df['publishedAt'], errors='coerce'
    )
    nat_count = df['publishedAt'].isna().sum()
    logger.info('convert_dates: %d rows could not be parsed (NaT)', nat_count)
    return df


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    int_cols = ['published_year']

    for col in int_cols:
        if col in df.columns:
            numeric_col = pd.to_numeric(df[col], errors='coerce')
            df[col] = numeric_col.round().astype('Int64')
            logger.info('convert_numeric_columns: %s -> Int64', col)

    return df


def convert_category_columns(df: pd.DataFrame) -> pd.DataFrame:
    cat_cols = ['source_name']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
            logger.info('convert_category_columns: %s -> category', col)
    return df


def memory_report(df_before: pd.DataFrame, df_after: pd.DataFrame) -> None:

    mb_before = df_before.memory_usage(deep=True).sum() / 1024**2
    mb_after  = df_after.memory_usage(deep=True).sum() / 1024**2
    saved = mb_before - mb_after
    pct   = (saved / mb_before * 100) if mb_before > 0 else 0
    logger.info('Memory before: %.2f MB', mb_before)
    logger.info('Memory after:  %.2f MB', mb_after)
    logger.info('Saved:         %.2f MB  (%.1f%%)', saved, pct)