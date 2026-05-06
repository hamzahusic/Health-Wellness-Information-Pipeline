import pandas as pd
import logging

logger = logging.getLogger(__name__)


def wide_to_long(df, id_vars, value_vars, var_name='metric', value_name='value'):
    long_df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name=value_name)
    logger.info('Wide->Long: %d rows x %d cols -> %d rows x %d cols',
                len(df), len(df.columns), len(long_df), len(long_df.columns))
    return long_df


def long_to_wide(df, index_col, columns_col, values_col):
    wide_df = df.pivot(index=index_col, columns=columns_col, values=values_col)
    wide_df.columns.name = None
    wide_df = wide_df.reset_index()
    logger.info('Long->Wide: %d rows x %d cols', len(wide_df), len(wide_df.columns))
    return wide_df


def build_pivot_table(df, values, index, columns, aggfunc='mean', fill_value=0, margins=False):
    pt = pd.pivot_table(df, values=values, index=index, columns=columns,
                        aggfunc=aggfunc, fill_value=fill_value, margins=margins)
    logger.info('Pivot table shape: %s', pt.shape)
    return pt


def build_crosstab(df, row_col, col_col, normalize=False):
    ct = pd.crosstab(df[row_col], df[col_col], margins=True, normalize=normalize)
    return ct


def articles_per_source_year(df):
    """Pivot table: article count by publish_year (rows) × source_name (columns)."""
    required = {'publish_year', 'source_name', 'title'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {missing}')
    pt = build_pivot_table(
        df,
        values='title',
        index='publish_year',
        columns='source_name',
        aggfunc='count',
        fill_value=0,
        margins=True,
    )
    logger.info('articles_per_source_year pivot: %s', pt.shape)
    return pt
