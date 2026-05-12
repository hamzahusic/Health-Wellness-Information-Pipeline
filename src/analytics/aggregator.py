import pandas as pd
import logging

logger = logging.getLogger(__name__)


def source_summary(df, source_col='source_name', content_col='content', author_col='author'):
    if source_col not in df.columns:
        logger.warning('source_col "%s" not found in DataFrame', source_col)
        return pd.DataFrame()

    agg_dict = {}
    agg_dict['article_count'] = (source_col, 'count')
    if content_col in df.columns:
        df = df.copy()
        df['_content_len'] = df[content_col].str.len().fillna(0)
        agg_dict['avg_content_length'] = ('_content_len', 'mean')
        agg_dict['total_content_length'] = ('_content_len', 'sum')
    if author_col in df.columns:
        agg_dict['unique_authors'] = (author_col, 'nunique')

    summary = df.groupby(source_col).agg(**agg_dict).reset_index()
    summary = summary.sort_values('article_count', ascending=False)
    logger.info('Source summary: %d sources', len(summary))
    return summary


def yearly_trends(df, year_col='publish_year', content_col='content', author_col='author'):
    if year_col not in df.columns:
        logger.warning('year_col "%s" not found in DataFrame', year_col)
        return pd.DataFrame()

    df = df[pd.to_numeric(df[year_col], errors='coerce').fillna(0) > 2000].copy()
    df['_content_len'] = df[content_col].str.len().fillna(0) if content_col in df.columns else 0

    agg_dict = {'article_count': (year_col, 'count')}
    if content_col in df.columns:
        agg_dict['avg_content_length'] = ('_content_len', 'mean')
    if author_col in df.columns:
        agg_dict['unique_authors'] = (author_col, 'nunique')

    trends = df.groupby(year_col).agg(**agg_dict).reset_index()
    trends = trends.sort_values(year_col)
    logger.info('Yearly trends: %d years', len(trends))
    return trends


def top_n_per_group(df, group_col, sort_col, n=5, ascending=False):
    result = (
        df.groupby(group_col, group_keys=False)
          .apply(lambda x: x.nlargest(n, sort_col) if not ascending
                 else x.nsmallest(n, sort_col))
    )
    logger.info('top_n_per_group: group=%s sort=%s n=%d -> %d rows', group_col, sort_col, n, len(result))
    return result
