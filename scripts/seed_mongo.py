"""
One-time script: load the cleaned articles CSV into MongoDB.

Run once before starting the dashboard:
    python scripts/seed_mongo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "articles_pipeline")

_BASE = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "cleaned")
CSV_PATH = None
for _name in ("articles_clean.csv", "articles_cleaned.csv"):
    _candidate = os.path.join(_BASE, _name)
    if os.path.exists(_candidate):
        CSV_PATH = _candidate
        break

if CSV_PATH is None:
    CSV_PATH = os.path.join(_BASE, "articles_clean.csv")  # will error with clear message


def seed():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows from {CSV_PATH}")

    client = MongoClient(MONGO_URI)
    col = client[DB_NAME]["raw_articles"]
    col.drop()

    records = df.where(df.notna(), None).to_dict("records")
    if records:
        col.insert_many(records)
        print(f"Inserted {len(records):,} documents into {DB_NAME}.raw_articles")

    col.create_index("source_name")
    col.create_index("published_year")
    col.create_index("title")
    col.create_index("Category")
    print("Indexes created.")
    client.close()


if __name__ == "__main__":
    seed()
