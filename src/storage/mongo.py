import logging
import os

from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
from PIL import Image

client = MongoClient("mongodb://localhost:27017/")
db = client["articles_pipeline"]
collection = db["raw_articles"]
image_metadata_collection = db["image_metadata"]
raw_audio_collection = db["raw_audio"]
raw_video_collection = db["raw_video"]
transcripts_collection = db["transcripts"]

def get_db():
    return db
    
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

def build_scraped_record(data, source_url, page_number=None):
    return {
        "data": data,
        "source": source_url,
        "page_number": page_number,
        "extracted_at": datetime.utcnow(),
        "type": "web_scraping"
    }

def build_ocr_record(text, source_file, page_number=None):
    return {
        "data": {"text": text},
        "source": source_file,
        "page_number": page_number,
        "extracted_at": datetime.utcnow(),
        "type": "ocr"
    }

def save_image_metadata(metadata_list):
    collection = image_metadata_collection
    for meta in metadata_list:
        meta['processed_at'] = datetime.utcnow().isoformat()  
        collection.update_one(
            {'filename': meta['filename']},  
            {'$set': meta},  
            upsert=True  
        )
    print(f'Saved {len(metadata_list)} image records to MongoDB')

def get_image_metadata(movie_id=None):
    query = {'movie_id': movie_id} if movie_id else {}
    return list(image_metadata_collection.find(query, {'_id': 0}))

def apply_image_metadata(image_path, movie_id=None):
    img = Image.open(image_path)
    width, height = img.size
    file_size = os.path.getsize(image_path)

    metadata = {
        'filename': Path(image_path).name,
        'movie_id': movie_id,
        'width': width,
        'height': height,
        'file_size': file_size
    }

    return metadata 

def process_images_and_save_metadata(image_paths, article_id=None):
    metadata_list = []
    for image_path in image_paths:
        img_metadata = apply_image_metadata(image_path, article_id)  
        metadata_list.append(img_metadata) 

    save_image_metadata(metadata_list) 

images_dir = '../../data/raw/images'
image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
image_paths = [os.path.join(images_dir, image_file) for image_file in image_files]
process_images_and_save_metadata(image_paths, article_id="article123")

def save_transcript(db, transcript_result: dict, source_path: str, source_type: str = 'audio', json_path: str = None, txt_path:  str = None, srt_path:  str = None) -> str:
    doc = {
        'source_file':           transcript_result.get('source_file', ''),
        'source_path':           source_path,
        'source_type':           source_type,
        'model':                 transcript_result.get('model', 'unknown'),
        'language':              transcript_result.get('language', ''),
        'language_probability':  transcript_result.get('language_probability', 0),
        'duration_s':            transcript_result.get('duration_s', 0),
        'full_text':             transcript_result.get('full_text', ''),
        'segments':              transcript_result.get('segments', []),
        'transcript_json_path':  json_path,
        'transcript_txt_path':   txt_path,
        'transcript_srt_path':   srt_path,
        'transcribed_at':        datetime.utcnow().isoformat(),
    }
    result = db['transcripts'].insert_one(doc)
    logging.getLogger(__name__).info(
        f'Saved transcript to MongoDB: {doc["source_file"]} '
        f'(id={result.inserted_id})'
    )
    return str(result.inserted_id)