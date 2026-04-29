import pandas as pd
import logging
from pathlib import Path

from cleaning.missing_handler import (
    drop_rows_missing_title,
    fill_missing_description,
)
from cleaning.string_cleaner import (
    clean_title,
    clean_description_text,
    extract_year_from_published_at,
)
from cleaning.deduplicator import (
    drop_exact_duplicates,
    drop_duplicate_ids,
)
from cleaning.type_converter import (
    convert_dates,
    convert_numeric_columns,
    convert_category_columns,
)
from cleaning.validator import run_all_validations

logger = logging.getLogger(__name__)
OUTPUT_PATH = Path('data/processed/cleaned/articles_clean.csv')


def run_cleaning_pipeline(df_raw: pd.DataFrame, save: bool = True) -> pd.DataFrame:
    logger.info('=== Starting cleaning pipeline: %d rows ===', len(df_raw))
    df = df_raw.copy()

    logger.info('Step 1: drop rows missing title')
    df = drop_rows_missing_title(df)

    logger.info('Step 2: drop exact duplicates')
    df = drop_exact_duplicates(df)

    logger.info('Step 3: drop duplicate urls')
    df = drop_duplicate_ids(df, id_col='url')

    logger.info('Step 4: clean string columns')
    df = clean_title(df)
    df = clean_description_text(df)

    logger.info('Step 5: extract published year from date string')
    df = extract_year_from_published_at(df)

    logger.info('Step 6: fill missing descriptions')
    df = fill_missing_description(df)

    logger.info('Step 7: convert data types')
    df = convert_dates(df)
    df = convert_numeric_columns(df)
    df = convert_category_columns(df)

    logger.info('Step 8: run validation')
    run_all_validations(df)

    if save:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False)
        logger.info('Saved clean dataset to %s (%d rows)', OUTPUT_PATH, len(df))

    logger.info('=== Cleaning pipeline complete: %d rows remain ===', len(df))
    return df