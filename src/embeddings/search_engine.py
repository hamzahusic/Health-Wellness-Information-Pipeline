import pandas as pd
from src.embeddings.chroma_store import get_chroma_client, get_collection


def semantic_search(query, n_results=10, filters=None, collection=None):
    """
    Search for health articles by meaning using ChromaDB.

    Args:
        query:      natural language search string
        n_results:  how many articles to return
        filters:    optional dict of ChromaDB where filters
        collection: existing ChromaDB collection (creates one if None)

    Returns:
        pandas DataFrame with columns: title, source_name, author,
        publish_year, similarity, text
    """
    if collection is None:
        client = get_chroma_client()
        collection = get_collection(client)

    kwargs = {"query_texts": [query], "n_results": min(n_results, collection.count())}
    if filters:
        kwargs["where"] = filters

    results = collection.query(**kwargs, include=["documents", "metadatas", "distances"])

    rows = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        rows.append({
            "title":        meta.get("title", ""),
            "source_name":  meta.get("source_name", ""),
            "author":       meta.get("author", ""),
            "publish_year": meta.get("publish_year", 0),
            "similarity":   round(1 - dist, 4),
            "text":         doc[:200],
        })
    return pd.DataFrame(rows)


def keyword_search(query, df, text_col="content", n_results=10):
    """
    Simple keyword search using string matching.
    Searches in the title AND the content column.

    Args:
        query:     search string (case insensitive)
        df:        pandas DataFrame with the article data
        text_col:  column to search in (default: content)
        n_results: maximum number of results to return

    Returns:
        pandas DataFrame with matching articles
    """
    query_lower = query.lower()
    mask = (
        df["title"].str.lower().str.contains(query_lower, na=False) |
        df[text_col].str.lower().str.contains(query_lower, na=False)
    )
    cols = [c for c in ["title", "source_name", "author", "publish_year"] if c in df.columns]
    results = df[mask][cols].copy()
    results["search_type"] = "keyword"
    return results.head(n_results).reset_index(drop=True)


def compare_search(query, df, collection=None, n_results=5):
    """
    Run both keyword and semantic search and show results side by side.

    Args:
        query:      search string
        df:         pandas DataFrame with article data (for keyword search)
        collection: ChromaDB collection (for semantic search)
        n_results:  number of results from each method

    Returns:
        dict with 'keyword' and 'semantic' DataFrames
    """
    kw = keyword_search(query, df, n_results=n_results)
    sem = semantic_search(query, n_results=n_results, collection=collection)

    print(f"--- Query: '{query}' ---")
    print()
    print(f"Keyword search found {len(kw)} results:")
    for _, row in kw.iterrows():
        print(f"  {row['title']} ({row.get('publish_year', '?')}) - {row.get('source_name', '?')}")

    print()
    print(f"Semantic search found {len(sem)} results:")
    for _, row in sem.iterrows():
        print(f"  [{row['similarity']:.3f}] {row['title']} ({row['publish_year']}) - {row['source_name']}")

    return {"keyword": kw, "semantic": sem}