import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Domain constants for news article data
MIN_PUBLISHED_YEAR = 2000
MAX_PUBLISHED_YEAR = 2030


def validate_no_null_titles(df: pd.DataFrame) -> None:
    assert df['title'].notna().all(), \
        f'Found {df["title"].isna().sum()} null titles'
    assert (df['title'].str.strip() != '').all(), \
        'Found rows with empty string titles'
    logger.info('validate_no_null_titles: PASSED')

def validate_url_format(df: pd.DataFrame) -> None:
    if 'url' not in df.columns:
        return
    non_null = df['url'].dropna().astype(str)
    valid = non_null.str.match(r'^https?://')
    assert valid.all(), \
        f'Found {(~valid).sum()} URLs with invalid format'
    logger.info('validate_url_format: PASSED')


def validate_published_year_range(df: pd.DataFrame) -> None:
    if 'published_year' not in df.columns:
        return
    non_null = df['published_year'].dropna()
    assert non_null.between(MIN_PUBLISHED_YEAR, MAX_PUBLISHED_YEAR).all(), \
        f'published_year out of range [{MIN_PUBLISHED_YEAR}, {MAX_PUBLISHED_YEAR}]'
    logger.info('validate_published_year_range: PASSED')


def validate_no_duplicate_ids(df: pd.DataFrame, id_col: str = 'url') -> None:
    if id_col not in df.columns:
        return
    dup_count = df.duplicated(subset=[id_col]).sum()
    assert dup_count == 0, \
        f'Found {dup_count} duplicate values in column {id_col}'
    logger.info('validate_no_duplicate_ids (%s): PASSED', id_col)


def validate_no_null_published_at(df: pd.DataFrame) -> None:
    if 'publishedAt' not in df.columns:
        return
    null_count = df['publishedAt'].isna().sum()
    assert null_count == 0, \
        f'Found {null_count} null values in publishedAt'
    logger.info('validate_no_null_published_at: PASSED')


def run_all_validations(df: pd.DataFrame) -> None:
    checks = [
        validate_no_null_titles,
        validate_url_format,
        validate_published_year_range,
        validate_no_duplicate_ids,
        validate_no_null_published_at,
    ]
    passed = 0
    failed = 0
    for check in checks:
        try:
            check(df)
            passed += 1
        except AssertionError as e:
            logger.error('FAILED: %s -> %s', check.__name__, e)
            failed += 1
    logger.info('Validation complete: %d passed, %d failed', passed, failed)