import requests
from bs4 import BeautifulSoup
import time
import os
import json
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "ResearchBot/1.0 (student-lab@ibu.edu.ba)"
}
RAW_HTML_DIR = "../../data/raw/html"
SCRAPED_JSON_DIR = "../../data/raw/scraped"

os.makedirs(RAW_HTML_DIR, exist_ok=True)
os.makedirs(SCRAPED_JSON_DIR, exist_ok=True)

def scrape_single_page(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    save_html("single_page.html", response.text)

    parsed = urlparse(url)
    main_path = f"{parsed.scheme}://{parsed.netloc}"

    soup = BeautifulSoup(response.text, "lxml")
    
    rows = soup.select("div.views-row.news-listing__item")

    results = []
  
    for row in rows:
        record = {
            "title":   row.select_one("h3.news-card__title a").get_text(strip=True)   if row.select_one("h3.news-card__title a")   else "",
            "published_date":  row.select_one("div.news-card__date").get_text(strip=True)   if row.select_one("div.news-card__date")   else "",
            "image_url":  main_path + row.select_one("img").get("src", "")   if row.select_one("img")   else "",
            "description": row.select_one("div.news-card__summary").get_text(strip=True) if row.select_one("div.news-card__summary") else "",
        }
        results.append(record)
    
    return results

def scrape_multiple_pages(base_url, max_pages=3):
    all_results = []

    parsed = urlparse(base_url)
    main_path = f"{parsed.scheme}://{parsed.netloc}"
    
    for page in range(0, max_pages):
        url = f"{base_url}&page={page}"
        print(f"Scraping page {page}: {url}")
        
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        save_html(f"news_page_{page}.html", response.text)
        
        soup = BeautifulSoup(response.text, "lxml")
        rows = soup.select("div.views-row.news-listing__item")
        
        for row in rows:
            record = {
                "title":   row.select_one("h3.news-card__title a").get_text(strip=True)   if row.select_one("h3.news-card__title a")   else "",
                "published_date":  row.select_one("div.news-card__date").get_text(strip=True)   if row.select_one("div.news-card__date")   else "",
                "image_url":  main_path + row.select_one("img").get("src", "")   if row.select_one("img")   else "",
                "description": row.select_one("div.news-card__summary").get_text(strip=True) if row.select_one("div.news-card__summary") else "",
            }
            all_results.append(record)
        
        time.sleep(1.5) 
    
    print(f"In total there is: {len(all_results)} news items scraped")
    save_json("news_multiple_pages.json", all_results)
    return all_results

def save_html(filename, html_text):
    path = os.path.join(RAW_HTML_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_text)

def save_json(filename, data):
    path = os.path.join(SCRAPED_JSON_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # url = "https://www.diabetes.org.uk/about-us/news-and-views/search?category=all&page=0"
    # data = scrape_single_page(url)
    # for item in data:
    #     print(item)
    # films = scrape_oscar_films(years=[2010, 2011, 2012])
    # for f in films[:3]:
    #     print(f)
    base_url = "https://www.diabetes.org.uk/about-us/news-and-views/search?category=all"
    scraped_data = scrape_multiple_pages(base_url, max_pages=3)
    # Print first few entries to verify
    for item in scraped_data[:5]:
        print(item)