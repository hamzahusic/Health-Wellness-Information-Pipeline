import pandas as pd
import numpy as np
import logging
logger = logging.getLogger(__name__)

def report_missing(df: pd.DataFrame) -> pd.DataFrame:
    missing_count = df.isna().sum()
    missing_pct = (df.isna().mean() * 100).round(2)
    report = pd.DataFrame({
        'missing_count': missing_count,
        'missing_pct': missing_pct,
        'dtype': df.dtypes
    })
    report = report[report['missing_count'] > 0].sort_values(
        'missing_pct', ascending=False
    )
    logger.info('Missing value report generated for %d columns', len(report))
    return report

def drop_rows_missing_title(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.dropna(subset=['title'])
    df = df[df['title'].str.strip() != '']
    after = len(df)
    dropped = before - after
    logger.info('drop_rows_missing_title: dropped %d rows', dropped)
    return df.reset_index(drop=True)

def drop_rows_missing_published_at(df: pd.DataFrame) -> pd.DataFrame:
    if 'publishedAt' not in df.columns:
        return df
    before = len(df)
    df = df.dropna(subset=['publishedAt'])
    after = len(df)
    logger.info('drop_rows_missing_published_at: dropped %d rows', before - after)
    return df.reset_index(drop=True)

def fill_missing_description(df: pd.DataFrame) -> pd.DataFrame:
    before = df['description'].isna().sum()
    df['description'] = df['description'].fillna('No description available.')
    logger.info('fill_missing_description: filled %d rows', before)
    return df

def replace_zero_with_nan(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            zeros = (df[col] == 0).sum()
            df[col] = df[col].replace(0, np.nan)
            logger.info('replace_zero_with_nan: %s -> replaced %d zeros', col, zeros)
    return df

def fill_numeric_with_median(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            median_val = df[col].median()
            filled = df[col].isna().sum()
            df[col] = df[col].fillna(median_val)
            logger.info('fill_numeric_with_median: %s -> filled %d with %.2f',
                        col, filled, median_val)
    return df


def drop_high_missingness_columns(df: pd.DataFrame, threshold: float = 0.6) -> pd.DataFrame:
    miss_ratio = df.isna().mean()
    to_drop = miss_ratio[miss_ratio > threshold].index.tolist()
    if to_drop:
        df = df.drop(columns=to_drop)
        logger.info('drop_high_missingness_columns: dropped %s', to_drop)
    return df