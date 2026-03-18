import csv
import xml.etree.ElementTree as ET
import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from storage.mongo import save_to_mongo 

def extract_articles_fields(article):
    return {
        "source_name": article.get("source_name") or article.get("source", {}).get("name"),
        "title": article.get("title"),
        "author": article.get("author"),
        "description": article.get("description"),
        "publishedAt": article.get("publishedAt"),
        "content": article.get("content")
    }

def parse_csv_file(file_path):
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)  
        for row in reader:
            # print(f"Source name: {row['source_name']}, Title: {row['title']}, Author: {row['author']}, Description: {row['description']}, Published At: {row['publishedAt']}, Content: {row['content']}")
            article_fields = extract_articles_fields(row)  
            print(f"Saving to MongoDB: {article_fields}")
            save_to_mongo(article_fields, "CSV Source")
            

def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    for item in root.findall("article"):
        article = {
            "source_name": item.find("source/name").text,
            "title": item.find("title").text,
            "author": item.find("author").text,
            "description": item.find("description").text,
            "publishedAt": item.find("publishedAt").text,
            "content": item.find("content").text
        }
        # print(f"Source Name: {article['source_name']}, Title: {article['title']}, Author: {article['author']}, Description: {article['description']}, Published At: {article['publishedAt']}, Content: {article['content']}")
        article_fields = extract_articles_fields(article) 
        print(f"Saving to MongoDB: {article_fields}")
        save_to_mongo(article_fields, "XML Source")

def parse_json_files():
    folder_path = "../../data/raw/api/"

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"): 
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r") as f:
                article_data = json.load(f)

            if isinstance(article_data, dict):  # If article_data is a dictionary (single article)
                article_fields = extract_articles_fields(article_data)
                # print(article_fields)
                print(f"Saving to MongoDB: {article_fields}")
                save_to_mongo(article_fields, filename)
            else:
                print(f"Unexpected structure in {filename}: {article_data}")

if __name__ == "__main__":
    parse_json_files()
    parse_csv_file("../../data/raw/csv/articles.csv")
    parse_xml_file("../../data/raw/xml/articles.xml")

