import requests
import os
import time
from dotenv import load_dotenv
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from utils.logger import logging

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
url = f"https://newsapi.org/v2/everything?q=diabetes&apiKey={API_KEY}"


def fetch_news(pages=3):
    all_articles = []

    for page in range(1, pages + 1):
        # Make the API request
        response = safe_request(url + f"&page={page}")
        
        if response:
            data = response.json()
            all_articles.extend(data["articles"])  # Append articles from this page
        else:
            print(f"Error occurred on page {page}. Skipping.")
            continue

    return all_articles

def safe_request(url, retries=3):
    for i in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Will raise an HTTPError for bad responses
            
            logging.info(f"Successfully fetched data from {url}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error on attempt {i + 1}: {e}")
            logging.error(f"Response: {response.text}")  # Log the full response if an error occurs
            
            time.sleep(2 ** i)  # Exponential backoff for retries

    logging.error(f"Failed after {retries} attempts.")
    return None

def save_raw_data(data, page_num):
    
    folder_path = "../../data/raw/api/"
    os.makedirs(folder_path, exist_ok=True)
    
    # Define the file path to store the data for each page
    filename = f"articles_page_{page_num}.json"
    file_path = os.path.join(folder_path, filename)
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Raw data saved to {file_path}")

# if __name__ == "__main__":
#    articles = fetch_news(pages=3) 
#    print(f"Fetched {len(articles)} articles.")
#    if articles:
#        print("Here are some article titles:")
#        for article in articles[:5]: 
#            print(article["title"])

if __name__ == "__main__":
    articles = fetch_news(3) 
    for page_num, article_data in enumerate(articles, start=1):
        save_raw_data(article_data, page_num)  