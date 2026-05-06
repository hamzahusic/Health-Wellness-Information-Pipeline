import pandas as pd
import logging

logger = logging.getLogger(__name__)


def q1_top_sources_by_volume(df, source_col='source_name', top_n=10):
    """Which sources publish the most articles?"""
    if source_col not in df.columns:
        logger.warning('q1: source_col "%s" missing', source_col)
        return pd.DataFrame()

    result = (
        df[source_col]
          .value_counts()
          .head(top_n)
          .reset_index()
          .rename(columns={source_col: 'source_name', 'count': 'article_count'})
    )
    logger.info('Q1 top sources by volume: %d rows', len(result))
    return result


def q2_avg_content_length_by_source(df, source_col='source_name', content_col='content', top_n=10):
    """Which sources produce the longest articles on average?"""
    if source_col not in df.columns or content_col not in df.columns:
        logger.warning('q2: required columns missing')
        return pd.DataFrame()

    df = df.copy()
    df['_content_len'] = df[content_col].str.len().fillna(0)

    result = (
        df.groupby(source_col)['_content_len']
          .mean()
          .nlargest(top_n)
          .reset_index()
          .rename(columns={'_content_len': 'avg_content_length'})
    )
    result['avg_content_length'] = result['avg_content_length'].round(1)
    logger.info('Q2 avg content length by source: %d rows', len(result))
    return result


def q3_yearly_volume(df, year_col='publish_year'):
    """How has article publication volume changed over time?"""
    if year_col not in df.columns:
        logger.warning('q3: year_col "%s" missing', year_col)
        return pd.DataFrame()

    result = (
        df[pd.to_numeric(df[year_col], errors='coerce').fillna(0) > 2000]
          .groupby(year_col)
          .size()
          .reset_index(name='article_count')
          .sort_values(year_col)
    )
    logger.info('Q3 yearly volume: %d years', len(result))
    return result


def q4_top_authors_by_volume(df, author_col='author', top_n=10):
    """Which authors contribute the most articles?"""
    if author_col not in df.columns:
        logger.warning('q4: author_col "%s" missing', author_col)
        return pd.DataFrame()

    result = (
        df[author_col]
          .dropna()
          .value_counts()
          .head(top_n)
          .reset_index()
          .rename(columns={author_col: 'author', 'count': 'article_count'})
    )
    logger.info('Q4 top authors by volume: %d rows', len(result))
    return result


def run_all_questions(df):
    """Run all four analytical questions and print a formatted summary."""
    results = {}

    print('\n===========================')
    print('ANALYTICAL FINDINGS SUMMARY')
    print('===========================\n')

    # Q1
    top_sources = q1_top_sources_by_volume(df)
    results['top_sources'] = top_sources
    if not top_sources.empty:
        best = top_sources.iloc[0]
        print(f'Q1 - Top Source by Volume: {best["source_name"]} '
              f'({best["article_count"]} articles)')
    else:
        print('Q1 - Top Source by Volume: no data')

    # Q2
    avg_lengths = q2_avg_content_length_by_source(df)
    results['avg_content_length_by_source'] = avg_lengths
    if not avg_lengths.empty:
        best = avg_lengths.iloc[0]
        print(f'Q2 - Longest Avg Content: {best["source_name"]} '
              f'({best["avg_content_length"]:,.1f} chars avg)')
    else:
        print('Q2 - Longest Avg Content: no data')

    # Q3
    yearly = q3_yearly_volume(df)
    results['yearly_volume'] = yearly
    if not yearly.empty:
        peak = yearly.loc[yearly['article_count'].idxmax()]
        print(f'Q3 - Peak Publication Year: {int(peak["publish_year"])} '
              f'({int(peak["article_count"])} articles)')
    else:
        print('Q3 - Peak Publication Year: no data')

    # Q4
    top_authors = q4_top_authors_by_volume(df)
    results['top_authors'] = top_authors
    if not top_authors.empty:
        best = top_authors.iloc[0]
        pct = best['article_count'] / len(df) * 100
        print(f'Q4 - Top Author: {best["author"]} '
              f'({best["article_count"]} articles, {pct:.1f}% of dataset)')
    else:
        print('Q4 - Top Author: no data')

    print('\n===========================')
    return results
