import numpy as np
import logging

logger = logging.getLogger(__name__)


def demonstrate_array_creation() -> dict:
    logger.info('Demonstrating NumPy array creation methods')
    popularity = np.array([120.4, 95.7, 80.2, 63.1, 55.8, 48.3])
    revenue_placeholder = np.zeros(6)
    genre_weights = np.ones((3, 4))   # 3 genres × 4 features
    years = np.arange(2010, 2025)     # 2010 … 2024
    score_buffer = np.empty((2, 3))

    logger.info('Array creation complete')
    return {
        'popularity':          popularity,
        'revenue_placeholder': revenue_placeholder,
        'genre_weights':       genre_weights,
        'years':               years,
        'score_buffer':        score_buffer,
    }


def print_array_info(arrays: dict) -> None:
    for name, arr in arrays.items():
        print(f'  {name:<22s} shape={str(arr.shape):<12} dtype={arr.dtype}  ndim={arr.ndim}  size={arr.size}')


def vectorized_operations(vote_avg: np.ndarray, vote_count: np.ndarray) -> dict:
    logger.info('Running vectorized operations')

    normalised = vote_avg * 10
    weighted   = vote_avg * np.log(vote_count)

    high_rated = vote_avg > 7.5
    quality    = (vote_avg > 7.0) & (vote_count > 1000)

    stats = {
        'mean':  float(vote_avg.mean()),
        'std':   float(vote_avg.std()),
        'max':   float(vote_avg.max()),
        'min_votes': int(vote_count.min()),
        'total_votes': int(vote_count.sum()),
    }

    logger.info('Vectorized operations complete: mean=%.2f', stats['mean'])
    return {
        'normalised':  normalised,
        'weighted':    np.round(weighted, 2),
        'high_rated':  high_rated,
        'quality':     quality,
        'stats':       stats,
    }


def axis_reductions(matrix: np.ndarray) -> dict:
    col_means = matrix.mean(axis=0)   # one mean per column
    row_means = matrix.mean(axis=1)   # one mean per row
    col_stds  = matrix.std(axis=0)
    return {
        'col_means': col_means,
        'row_means': row_means,
        'col_stds':  col_stds,
    }


def broadcasting_example(vote_avg: np.ndarray) -> np.ndarray:
    min_v, max_v = vote_avg.min(), vote_avg.max()
    if max_v == min_v:
        return np.zeros_like(vote_avg, dtype=float)
    return (vote_avg - min_v) / (max_v - min_v)