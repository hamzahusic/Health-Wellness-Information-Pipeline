import pandas as pd
import logging

logger = logging.getLogger(__name__)


def merge_mysql_mongodb(mysql_df, mongo_df, on='url', how='inner'):
    logger.info('Merging MySQL (%d rows) and MongoDB (%d rows) on "%s" with how="%s"',
                len(mysql_df), len(mongo_df), on, how)

    mysql_df = mysql_df.copy()
    mongo_df = mongo_df.copy()
    mysql_df[on] = mysql_df[on].astype(str)
    mongo_df[on] = mongo_df[on].astype(str)

    merged = pd.merge(
        mysql_df,
        mongo_df,
        on=on,
        how=how,
        suffixes=('_mysql', '_mongo')
    )

    logger.info('Merged result: %d rows, %d columns', len(merged), len(merged.columns))
    return merged


def demonstrate_join_types(mysql_df, mongo_df, on='url'):
    results = {}
    for how in ['inner', 'left', 'right', 'outer']:
        merged = pd.merge(mysql_df, mongo_df, on=on, how=how)
        results[how] = len(merged)
        print(f'  {how:6s} join -> {len(merged):5d} rows')
    return results


def concat_dataframes(dfs, reset_index=True):
    combined = pd.concat(dfs, axis=0, ignore_index=reset_index)
    logger.info('Concatenated %d DataFrames into %d rows', len(dfs), len(combined))
    return combined
