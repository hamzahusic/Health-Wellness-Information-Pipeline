import re
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Pre-compiled patterns
_HEALTH_TERMS   = re.compile(
    r'\b(?:health|wellness|diet|nutrition|exercise|mental\s+health|diabetes|'
    r'obesity|vaccine|cancer|therapy|fitness|sleep|stress|anxiety|depression)\b',
    re.IGNORECASE,
)
_SOURCE_ID      = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
RE_PUBLISHED_AT = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$')


def filter_titles_starting_with(df: pd.DataFrame, prefix: str = 'The') -> pd.DataFrame:
    pattern = rf'^{re.escape(prefix)}\s'
    mask    = df['title'].str.contains(pattern, na=False)
    result  = df[mask]
    logger.info('Titles starting with "%s": %d', prefix, len(result))
    return result


def extract_number_from_title(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['title_number'] = df['title'].str.extract(r'(\d+)', expand=False)
    count = df['title_number'].notna().sum()
    logger.info('Titles containing a number: %d', count)
    return df


def health_keyword_count(df: pd.DataFrame) -> int:
    if 'content' not in df.columns:
        return 0
    mask  = df['content'].str.contains(_HEALTH_TERMS.pattern, case=False, na=False, regex=True)
    count = int(mask.sum())
    logger.info('Articles with health keywords: %d', count)
    return count


def short_descriptions(df: pd.DataFrame, max_chars: int = 20) -> pd.DataFrame:
    if 'description' not in df.columns:
        return df.iloc[0:0]
    mask   = df['description'].str.len() < max_chars
    result = df.loc[mask, [c for c in ['title', 'description'] if c in df.columns]]
    logger.info('Very short descriptions (<%d chars): %d', max_chars, len(result))
    return result


def flag_short_descriptions(df: pd.DataFrame, min_words: int = 5) -> pd.Series:
    if 'description' not in df.columns:
        return pd.Series(False, index=df.index)
    word_count = df['description'].str.split().str.len().fillna(0)
    short = word_count < min_words
    logger.info('flag_short_descriptions: %d descriptions have fewer than %d words', short.sum(), min_words)
    return short


def find_invalid_published_at(df: pd.DataFrame) -> pd.Series:
    col = 'publishedAt'
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    has_value    = df[col].notna()
    wrong_format = has_value & ~df[col].astype(str).str.match(RE_PUBLISHED_AT.pattern, na=False)
    logger.info('find_invalid_published_at: %d values have wrong format', wrong_format.sum())
    return wrong_format


def validate_source_id(id_str: str) -> bool:
    return bool(_SOURCE_ID.match(str(id_str).strip()))


def extract_number_from_string(series: pd.Series) -> pd.Series:
    return series.str.extract(r'(\d+\.?\d*)', expand=False).astype(float)