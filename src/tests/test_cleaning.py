import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cleaning.missing_handler import (
    drop_rows_missing_title,
    fill_missing_description,
)
from src.cleaning.string_cleaner import (
    clean_title,
    clean_description_text,
    extract_year_from_published_at,
)
from src.cleaning.deduplicator import (
    drop_exact_duplicates,
    drop_duplicate_ids,
    count_duplicates,
)
from src.cleaning.type_converter import convert_dates
from src.cleaning.validator import (
    validate_no_null_titles,
    validate_url_format,
)


@pytest.fixture
def sample_articles():
    """Small DataFrame matching the real NewsAPI article schema.
    Intentionally includes problems we want to test fixing.
    """
    return pd.DataFrame({
        'url':         [
            'https://npr.org/article1',
            'https://webmd.com/article2',
            'https://healthline.com/article3',
            'https://bbc.com/article4',
            'https://mayoclinic.org/article5',
        ],
        'title':       ['Health Study Shows Results', '  Ozempic Benefits  ',
                        None, 'Diet Tips', ''],
        'description': ['A new study found key results.', None,
                        'Short.', 'Eat well daily.', 'Another article here.'],
        'source_name': ['NPR', 'WebMD', 'Healthline', 'BBC Health', 'Mayo Clinic'],
        'author':      ['Jane Doe', 'John Smith', None, 'Alice', 'Bob'],
        'publishedAt': ['2026-03-10T10:00:00Z', '2026-03-08T08:30:00Z',
                        '2025-01-01T00:00:00Z', 'BAD_DATE', None],
        'content':     ['Content A...', 'Content B...', 'Content C...',
                        'Content D...', 'Content E...'],
    })


def test_drop_rows_missing_title_removes_null(sample_articles):
    result = drop_rows_missing_title(sample_articles)
    assert result['title'].isna().sum() == 0


def test_drop_rows_missing_title_removes_empty_string(sample_articles):
    result = drop_rows_missing_title(sample_articles)
    assert (result['title'].str.strip() == '').sum() == 0


def test_fill_missing_description_no_nulls_remain(sample_articles):
    result = fill_missing_description(sample_articles)
    assert result['description'].isna().sum() == 0


def test_fill_missing_description_uses_placeholder(sample_articles):
    result = fill_missing_description(sample_articles)
    filled = result.loc[sample_articles['description'].isna(), 'description']
    assert filled.str.contains('available', case=False).all()


def test_clean_title_strips_whitespace(sample_articles):
    result = clean_title(sample_articles.dropna(subset=['title']))
    assert not result['title'].str.startswith(' ').any()
    assert not result['title'].str.endswith(' ').any()


def test_clean_description_text_removes_html(sample_articles):
    df = sample_articles.copy()
    df.loc[0, 'description'] = '  <b>Bold claim</b>  about health.  '
    result = clean_description_text(df)
    assert '<b>' not in result.loc[0, 'description']
    assert not result.loc[0, 'description'].startswith(' ')


def test_extract_year_creates_column(sample_articles):
    result = extract_year_from_published_at(sample_articles)
    assert 'published_year' in result.columns


def test_extract_year_correct_values(sample_articles):
    result = extract_year_from_published_at(sample_articles)
    assert result.loc[0, 'published_year'] == 2026
    assert result.loc[1, 'published_year'] == 2026
    assert result.loc[2, 'published_year'] == 2025


def test_extract_year_bad_date_becomes_null(sample_articles):
    result = extract_year_from_published_at(sample_articles)
    assert pd.isna(result.loc[3, 'published_year'])
    assert pd.isna(result.loc[4, 'published_year'])


def test_drop_exact_duplicates_removes_copies():
    df = pd.DataFrame({
        'url':   ['https://a.com', 'https://a.com', 'https://b.com'],
        'title': ['Article A', 'Article A', 'Article B'],
    })
    result = drop_exact_duplicates(df)
    assert len(result) == 2


def test_drop_duplicate_ids_keeps_first():
    df = pd.DataFrame({
        'url':   ['https://a.com', 'https://a.com', 'https://b.com'],
        'title': ['Version A', 'Version B', 'Other'],
    })
    result = drop_duplicate_ids(df, id_col='url')
    assert len(result) == 2
    assert result.loc[result['url'] == 'https://a.com', 'title'].values[0] == 'Version A'


def test_count_duplicates_returns_correct_number():
    df = pd.DataFrame({'url': ['https://a.com', 'https://a.com', 'https://a.com',
                                'https://b.com', 'https://c.com']})
    assert count_duplicates(df, col='url') == 2


def test_convert_dates_produces_datetime_type(sample_articles):
    result = convert_dates(sample_articles)
    assert pd.api.types.is_datetime64_any_dtype(result['publishedAt'])


def test_convert_dates_bad_values_become_nat(sample_articles):
    result = convert_dates(sample_articles)
    nat_count = result['publishedAt'].isna().sum()
    assert nat_count >= 2


def test_validate_no_null_titles_passes_on_clean_data():
    df = pd.DataFrame({'title': ['Health Article', 'Diet Study']})
    validate_no_null_titles(df)


def test_validate_no_null_titles_fails_on_null():
    df = pd.DataFrame({'title': ['Health Article', None]})
    with pytest.raises(AssertionError):
        validate_no_null_titles(df)


def test_validate_url_format_passes_on_valid_urls():
    df = pd.DataFrame({'url': ['https://npr.org/a', 'http://bbc.com/b']})
    validate_url_format(df)


def test_validate_url_format_fails_on_bad_url():
    df = pd.DataFrame({'url': ['https://valid.com', 'not-a-url']})
    with pytest.raises(AssertionError):
        validate_url_format(df)
