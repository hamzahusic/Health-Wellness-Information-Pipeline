import pandas as pd
import logging

logger = logging.getLogger(__name__)


def build_source_pipeline(min_article_count=5, top_n=10):
    pipeline = [
        # Stage 1: require a source name and content
        {
            '$match': {
                'source_name': {'$exists': True, '$ne': ''},
                'content':     {'$exists': True, '$ne': ''}
            }
        },
        # Stage 2: compute content length per document
        {
            '$addFields': {
                'content_length': {'$strLenCP': '$content'}
            }
        },
        # Stage 3: group by source
        {
            '$group': {
                '_id':                '$source_name',
                'article_count':      {'$sum': 1},
                'avg_content_length': {'$avg': '$content_length'},
                'unique_authors':     {'$addToSet': '$author'}
            }
        },
        # Stage 4: filter sources with enough articles
        {
            '$match': {
                'article_count': {'$gte': min_article_count}
            }
        },
        # Stage 5: sort by article count descending
        {
            '$sort': {'article_count': -1}
        },
        # Stage 6: limit to top N
        {
            '$limit': top_n
        },
        # Stage 7: reshape output fields
        {
            '$project': {
                '_id':                0,
                'source_name':        '$_id',
                'article_count':      1,
                'avg_content_length': {'$round': ['$avg_content_length', 1]},
                'unique_author_count': {'$size': '$unique_authors'}
            }
        }
    ]
    logger.info('Built source pipeline: min_article_count=%d, top_n=%d', min_article_count, top_n)
    return pipeline


def run_pipeline(collection, pipeline):
    cursor = collection.aggregate(pipeline)
    results = list(cursor)
    df = pd.DataFrame(results)
    logger.info('Pipeline returned %d documents', len(df))
    return df


def build_yearly_pipeline(start_year=2010):
    pipeline = [
        {
            '$match': {
                'publish_year': {'$gte': start_year},
                'title':        {'$exists': True, '$ne': ''}
            }
        },
        {
            '$group': {
                '_id':                '$publish_year',
                'article_count':      {'$sum': 1},
                'unique_sources':     {'$addToSet': '$source_name'},
                'unique_authors':     {'$addToSet': '$author'}
            }
        },
        {
            '$sort': {'_id': 1}
        },
        {
            '$project': {
                '_id':                 0,
                'publish_year':        '$_id',
                'article_count':       1,
                'unique_source_count': {'$size': '$unique_sources'},
                'unique_author_count': {'$size': '$unique_authors'}
            }
        }
    ]
    logger.info('Built yearly pipeline: start_year=%d', start_year)
    return pipeline
