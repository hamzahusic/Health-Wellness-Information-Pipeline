import os
import time
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv  
from urllib.parse import urlparse

load_dotenv()
logger = logging.getLogger(__name__)

NEWSAPI_BASE_URL = os.getenv('NEWSAPI_BASE_URL')
API_KEY = os.getenv('NEWS_API_KEY')

 
def fetch_popular_articles(pages=1):
    articles = []
    for page in range(1, pages + 1):
        url = f'{NEWSAPI_BASE_URL}/everything?q=diabetes&apiKey={API_KEY}&page={page}'
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        articles.extend(data.get('articles', []))
        logger.info(f'Fetched page {page}, total so far: {len(articles)}')
        time.sleep(0.5)  
    return articles
 
def download_poster(file_path, dest_dir):
    if not file_path:
        return None
    
    parsed = urlparse(file_path)
    filename = Path(parsed.path).name or parsed.netloc

    if not filename:
        filename = 'image'

    dest = Path(dest_dir) / filename
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        logger.debug(f'Already exists: {dest}')
        return str(dest)
    
    url = file_path
    resp = requests.get(url, stream=True, timeout=15)

    resp.raise_for_status()

    with open(dest, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info(f'Downloaded: {dest}')

    return str(dest)
 
def download_article_posters(articles, dest_dir='../../data/raw/images'):
    downloaded = []  
    for article in articles:
        poster_path = article.get('urlToImage')
        if poster_path: 
            local = download_poster(poster_path, dest_dir)  
            print(f"Saving images to: {os.path.abspath(dest_dir)}")
            if local:
                downloaded.append({
                    'article_id': article.get('url'),
                    'title': article['title'],
                    'local_path': local,
                    'poster_path': poster_path
                })
        time.sleep(0.1)  

    logger.info(f"Downloaded {len(downloaded)} posters.")
    return downloaded