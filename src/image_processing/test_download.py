import logging
logging.basicConfig(level=logging.INFO)
from downloader import fetch_popular_articles, download_article_posters

# Fetch 20 popular articles
articles = fetch_popular_articles(pages=1)
print(f'Fetched {len(articles)} articles')

# Download posters for the first 5 articles
results = download_article_posters(articles[:50], dest_dir='../../data/raw/images')

if results:  
    for r in results:
        print(r['title'], '->', r['local_path'])
else:
    print("No posters were downloaded.")

