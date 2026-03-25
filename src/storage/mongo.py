from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["articles_pipeline"]
collection = db["raw_articles"]
    
def save_to_mongo(data, source_url, extra_metadata=None):
    document = {
        "data": data,
        "source": source_url,
        "fetched_at": datetime.utcnow(),
        "version": 1
    }

    # additional metadata for documents
    if extra_metadata:
        document.update(extra_metadata)

    collection.insert_one(document)