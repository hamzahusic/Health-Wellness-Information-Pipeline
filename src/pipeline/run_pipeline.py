import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging  
from storage.mongo import save_to_mongo 
from api.client import fetch_news
from parsing.parsers import extract_articles_fields

def run_pipeline():
    articles = fetch_news(3)

    for article in articles:
        parsed = extract_articles_fields(article)

        save_to_mongo(parsed, "news_api")

    logging.info("Pipeline finished successfully")

if __name__ == "__main__":
    run_pipeline()