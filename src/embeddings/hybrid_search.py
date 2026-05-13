import pandas as pd
from src.embeddings.search_engine import keyword_search, semantic_search


def reciprocal_rank_fusion(kw_results, sem_results, k=60):
    """
    Combine two ranked lists using Reciprocal Rank Fusion.

    Args:
        kw_results:  DataFrame from keyword_search() with a 'title' column
        sem_results: DataFrame from semantic_search() with a 'title' column
        k:           constant to prevent extreme scores (default 60)

    Returns:
        DataFrame sorted by combined RRF score (highest first)
    """
    scores = {}
    metadata = {}

    for rank, (_, row) in enumerate(kw_results.iterrows()):
        title = row["title"]
        scores[title]   = scores.get(title, 0) + 1.0 / (k + rank + 1)
        metadata[title] = row.to_dict()

    for rank, (_, row) in enumerate(sem_results.iterrows()):
        title = row["title"]
        scores[title]   = scores.get(title, 0) + 1.0 / (k + rank + 1)
        if title not in metadata:
            metadata[title] = row.to_dict()

    rows = []
    for title, score in sorted(scores.items(), key=lambda x: -x[1]):
        row = metadata[title].copy()
        row["rrf_score"] = round(score, 6)
        rows.append(row)

    return pd.DataFrame(rows)


def hybrid_search(query, df, collection, n_results=10, k=60):
    """
    Run keyword and semantic search then combine with RRF.

    Args:
        query:      search string
        df:         pandas DataFrame of health articles for keyword search
        collection: ChromaDB collection for semantic search
        n_results:  final number of results to return
        k:          RRF constant

    Returns:
        DataFrame of top articles ranked by combined score
    """

    n_candidates = n_results * 3
    kw  = keyword_search(query, df,  n_results=n_candidates)
    sem = semantic_search(query,       n_results=n_candidates, collection=collection)

    combined = reciprocal_rank_fusion(kw, sem, k=k)
    return combined.head(n_results).reset_index(drop=True)