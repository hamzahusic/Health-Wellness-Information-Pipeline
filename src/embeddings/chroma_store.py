import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import pandas as pd
from pathlib import Path
from .embedder import build_article_text

# Path where ChromaDB saves data on disk
CHROMA_PATH = Path("../../data/embeddings/chroma_db")
COLLECTION_NAME = "health_articles"


def get_chroma_client():
    """
    Return a persistent ChromaDB client.
    Data is stored in data/embeddings/chroma_db/ and survives notebook restarts.
    """
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_PATH))


def get_collection(client=None, reset=False):
    """
    Get or create the health_articles collection.

    Args:
        client: a ChromaDB client (creates one if not provided)
        reset: if True, deletes the existing collection and starts fresh

    Returns:
        ChromaDB collection object
    """
    if client is None:
        client = get_chroma_client()

    # Use the same model as embedder.py so vectors are compatible
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def add_articles_to_collection(df, collection, batch_size=100):
    """
    Add health articles from a pandas DataFrame to the ChromaDB collection.

    Each article becomes one document. The text combines title, description,
    and content. Metadata stores structured fields for filtered search
    (e.g., only articles from a specific source or year).

    Args:
        df: cleaned articles DataFrame
        collection: ChromaDB collection
        batch_size: how many articles to add in one API call
    """
    existing_ids = set(collection.get()["ids"])
    print(f"Collection already has {len(existing_ids)} articles")

    documents, metadatas, ids = [], [], []

    for _, row in df.iterrows():
        if 'url' in row and str(row['url']) not in ('nan', ''):
            article_id = str(row['url'])[:500]
        else:
            article_id = f"article_{row.name}"

        if article_id in existing_ids:
            continue  # skip articles already in the collection

        text = build_article_text(row)
        if not text or text == 'Unknown article':
            continue

        meta = {
            "title":       str(row.get("title", "Unknown"))[:500],
            "source_name": str(row.get("source_name", "Unknown"))[:255],
            "author":      str(row.get("author", "Unknown"))[:255],
            "publish_year": int(row["publish_year"]) if pd.notna(row.get("publish_year")) and row.get("publish_year", 0) != 0
                            else (int(row["published_year"]) if pd.notna(row.get("published_year")) else 0),
        }

        documents.append(text)
        metadatas.append(meta)
        ids.append(article_id)

        # Add in batches to avoid memory issues with large datasets
        if len(documents) >= batch_size:
            collection.add(documents=documents, metadatas=metadatas, ids=ids)
            documents, metadatas, ids = [], [], []

    # Add any remaining articles
    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)

    total = collection.count()
    print(f"Collection now contains {total} articles")
    return total