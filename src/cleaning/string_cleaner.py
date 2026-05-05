import re
import pandas as pd
import logging
logger = logging.getLogger(__name__)

# Pre-compile regex patterns for speed
# These are compiled once when the module is loaded
RE_MULTI_SPACE = re.compile(r'\s+')
RE_YEAR_PARENS = re.compile(r'\(\d{4}\)')
RE_SPECIAL_CHARS = re.compile(r'[^\w\s\-\'\"\.,!?:]')

def clean_title(df: pd.DataFrame) -> pd.DataFrame:
    if 'title' not in df.columns:
        return df
    before = df['title'].copy()
    df['title'] = (
        df['title']
        .str.strip()
        .str.replace(RE_MULTI_SPACE, ' ', regex=True)
        .str.replace(RE_YEAR_PARENS, '', regex=True)
        .str.strip()   # strip again after removing year
    )
    changed = (before != df['title']).sum()
    logger.info('clean_title: %d titles modified', changed)
    return df

def clean_language_code(df: pd.DataFrame) -> pd.DataFrame:
    col = 'original_language'
    if col not in df.columns:
        return df
    df[col] = df[col].str.strip().str.lower()
    logger.info('clean_language_code: normalised to lowercase')
    return df

def clean_description_text(df: pd.DataFrame) -> pd.DataFrame:
    if 'description' not in df.columns:
        return df
    # Remove any HTML tags from scraped data
    RE_HTML = re.compile(r'<[^>]+>')
    df['description'] = (
        df['description']
        .str.strip()
        .str.replace(RE_HTML, ' ', regex=True)
        .str.replace(RE_MULTI_SPACE, ' ', regex=True)
        .str.strip()
    )
    logger.info('clean_description_text: description column cleaned')
    return df

def extract_year_from_published_at(df: pd.DataFrame) -> pd.DataFrame:
    if 'publishedAt' not in df.columns:
        return df
    col = df['publishedAt']
    if hasattr(col, 'dt'):
        df['published_year'] = col.dt.year.astype('Int64')
    else:
        df['published_year'] = (
            col.astype(str)
            .str.extract(r'^(\d{4})', expand=False)
            .astype('Int64', errors='ignore')
        )
    valid_years = df['published_year'].notna().sum()
    logger.info('extract_year_from_published_at: extracted %d years', valid_years)
    return df

def clean_source_name(df: pd.DataFrame, col: str = 'source_name') -> pd.DataFrame:
    if col not in df.columns:
        return df
    df[col] = (
        df[col]
        .str.strip()
        .str.replace(r'\s*,\s*', ', ', regex=True)
    )
    logger.info('clean_source_name: %s column normalised', col)
    return df