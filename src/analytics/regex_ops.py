"""
src/analytics/regex_ops.py
Regular-expression operations on articles pipeline text columns.
Uses both the re module and the pandas .str accessor.
"""
import re
import pandas as pd
import collections
import logging

logger = logging.getLogger(__name__)

# Pre-compiled patterns
_HEALTH_TERMS  = re.compile(
    r'\b(health|wellness|diet|nutrition|exercise|mental\s+health|diabetes|'
    r'obesity|vaccine|cancer|therapy|fitness|sleep|stress|anxiety|depression)\b',
    re.IGNORECASE,
)
_URL_DOMAIN    = re.compile(r'https?://(?:www\.)?([^/\s]+)')
_EXTRA_SPACE   = re.compile(r'\s+')
_SOURCE_ID     = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def filter_titles_starting_with(df: pd.DataFrame, prefix: str = 'The') -> pd.DataFrame:
    """Filter articles whose title starts with prefix (case-sensitive)."""
    pattern = rf'^{re.escape(prefix)}\s'
    mask    = df['title'].str.contains(pattern, na=False)
    result  = df[mask]
    logger.info('Titles starting with "%s": %d', prefix, len(result))
    return result


def extract_domain_from_url(urls: pd.Series) -> pd.Series:
    """
    Extract the domain from a URL Series.
    Example: 'https://www.bbc.com/health/...' → 'bbc.com'
    """
    result = urls.str.extract(_URL_DOMAIN.pattern, expand=False)
    logger.info('URLs with extractable domain: %d', result.notna().sum())
    return result


def health_keyword_count(df: pd.DataFrame) -> int:
    """Count articles whose content mentions at least one health/wellness term."""
    if 'content' not in df.columns:
        return 0
    mask  = df['content'].str.contains(_HEALTH_TERMS.pattern,
                                        case=False, na=False, regex=True)
    count = int(mask.sum())
    logger.info('Articles with health keywords: %d', count)
    return count


def short_content(df: pd.DataFrame, max_chars: int = 100) -> pd.DataFrame:
    """Return rows where content is shorter than max_chars characters."""
    if 'content' not in df.columns:
        return df.iloc[0:0]
    mask   = df['content'].str.len() < max_chars
    result = df.loc[mask, [c for c in ['title', 'source_name', 'content'] if c in df.columns]]
    logger.info('Very short content (<%d chars): %d', max_chars, len(result))
    return result


def normalize_author(authors: pd.Series) -> pd.Series:
    """
    Strip leading/trailing whitespace and collapse internal runs of
    whitespace in author names.
    Example: '  Jane  Doe  ' → 'Jane Doe'
    """
    result = (
        authors
        .str.strip()
        .str.replace(_EXTRA_SPACE.pattern, ' ', regex=True)
    )
    changed = (result != authors).sum()
    logger.info('Author names normalized: %d', changed)
    return result


def extract_numbers_from_content(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'first_number' column with the first digit sequence found
    in the content (e.g. a statistic like '42' or '3.5').
    """
    df = df.copy()
    if 'content' not in df.columns:
        return df
    df['first_number'] = df['content'].str.extract(r'(\d+(?:\.\d+)?)', expand=False)
    count = df['first_number'].notna().sum()
    logger.info('Articles containing a number in content: %d', count)
    return df


def top_health_keywords(df: pd.DataFrame, n: int = 15) -> list:
    """
    Find all health keyword matches across the content column and return
    the top-n as a list of (keyword, count) tuples.
    """
    if 'content' not in df.columns:
        return []
    all_matches: list = []
    df['content'].dropna().apply(
        lambda text: all_matches.extend(
            m.lower() for m in _HEALTH_TERMS.findall(text)
        )
    )
    return collections.Counter(all_matches).most_common(n)


def validate_source_id(id_str: str) -> bool:
    """
    Return True if id_str is a valid NewsAPI source ID:
    lowercase alphanumeric tokens joined by hyphens (e.g. 'bbc-news').
    """
    return bool(_SOURCE_ID.match(str(id_str).strip()))
