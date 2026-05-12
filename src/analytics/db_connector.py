import pymysql
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_connection(host='localhost', user='root', password='root', database='health_pipeline'):
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    logger.info('Connected to MySQL database: %s', database)
    return conn


def populate_articles(conn, df):
    required = ['source_id', 'title', 'source_name', 'author', 'publishedAt',
                'description', 'content', 'url', 'publish_year']
    available = [c for c in required if c in df.columns]
    data = df[available].dropna(subset=['title']).copy()

    if 'publishedAt' in data.columns:
        data['publishedAt'] = pd.to_datetime(data['publishedAt'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

    if 'publish_year' in data.columns:
        data['publish_year'] = pd.to_numeric(data['publish_year'], errors='coerce').astype('Int64')

    cursor = conn.cursor()
    inserted = 0
    skipped = 0

    for _, row in data.iterrows():
        try:
            cursor.execute(
                """
                INSERT IGNORE INTO health_articles
                    (source_id, title, source_name, author, publishedAt,
                     description, content, url, publish_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(row.get('source_id', '')) or None,
                    str(row.get('title', '')),
                    str(row.get('source_name', '')) or None,
                    str(row.get('author', '')) or None,
                    row.get('publishedAt') or None,
                    str(row.get('description', '')) or None,
                    str(row.get('content', '')) or None,
                    str(row.get('url', '')) or None,
                    int(row['publish_year']) if pd.notna(row.get('publish_year')) else None,
                )
            )
            inserted += 1
        except Exception as e:
            logger.warning('Skipped row title=%s: %s', row.get('title'), e)
            skipped += 1

    conn.commit()
    cursor.close()
    logger.info('Inserted %d rows, skipped %d rows', inserted, skipped)
    return inserted, skipped


def query_articles(conn, sql=None):
    if sql is None:
        sql = 'SELECT * FROM health_articles'
    df = pd.read_sql(sql, conn)
    logger.info('Queried %d rows from MySQL', len(df))
    return df
