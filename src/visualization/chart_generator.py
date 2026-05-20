"""
Automated chart generation module – Lab 12.
Loads the cleaned articles dataset and generates all static and interactive charts.
"""

import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = _PROJECT_ROOT / "data" / "processed" / "cleaned" / "articles_clean.csv"
STATIC_OUT = _PROJECT_ROOT / "outputs" / "visualizations" / "static"
INTERACTIVE_OUT = _PROJECT_ROOT / "outputs" / "visualizations" / "interactive"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load and lightly prepare the cleaned articles dataset."""
    if not path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at '{path}'. "
            "Run the cleaning pipeline first (Lab 9)."
        )
    df = pd.read_csv(path, low_memory=False)
    required = ["title", "source_name", "author", "content", "published_year"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")
    logger.info("Loaded %d articles from %s", len(df), path)
    return df


def run_static_charts(df: pd.DataFrame) -> dict:
    """Generate and save all matplotlib / seaborn charts."""
    from .static_charts import (
        plot_top_sources_by_count,
        plot_articles_over_years,
        plot_source_count_vs_length,
        plot_content_length_distribution,
        plot_content_length_by_source,
        plot_source_year_heatmap,
        plot_top_authors_by_count,
        plot_dashboard_subplots,
    )

    STATIC_OUT.mkdir(parents=True, exist_ok=True)
    results = {}

    charts = [
        ("top_sources_by_count",        plot_top_sources_by_count),
        ("articles_over_years",         plot_articles_over_years),
        ("source_count_vs_length",      plot_source_count_vs_length),
        ("content_length_distribution", plot_content_length_distribution),
        ("content_length_by_source",    plot_content_length_by_source),
        ("source_year_heatmap",         plot_source_year_heatmap),
        ("top_authors_by_count",        plot_top_authors_by_count),
        ("dashboard_subplots",          plot_dashboard_subplots),
    ]

    for name, fn in charts:
        try:
            paths = fn(df, out_dir=STATIC_OUT)
            results[name] = paths
            print(f"  [static]  {name}")
            print(f"            PNG → {paths['png']}")
            print(f"            PDF → {paths['pdf']}")
        except Exception as exc:
            logger.error("Failed to generate '%s': %s", name, exc)
            print(f"  [static]  {name}  FAILED: {exc}")

    return results


def run_interactive_charts(df: pd.DataFrame) -> dict:
    """Generate and save all Plotly interactive charts."""
    from .interactive_charts import (
        interactive_content_length_scatter,
        interactive_top_sources_bar,
        interactive_articles_per_year,
        interactive_source_content_boxplot,
        interactive_multi_layout,
    )

    INTERACTIVE_OUT.mkdir(parents=True, exist_ok=True)
    results = {}

    charts = [
        ("content_length_scatter", interactive_content_length_scatter),
        ("top_sources_bar",        interactive_top_sources_bar),
        ("articles_per_year",      interactive_articles_per_year),
        ("source_content_boxplot", interactive_source_content_boxplot),
        ("multi_layout",           interactive_multi_layout),
    ]

    for name, fn in charts:
        try:
            html_path = fn(df, out_dir=INTERACTIVE_OUT)
            results[name] = html_path
            print(f"  [interactive]  {name}")
            print(f"                 HTML → {html_path}")
        except Exception as exc:
            logger.error("Failed to generate '%s': %s", name, exc)
            print(f"  [interactive]  {name}  FAILED: {exc}")

    return results


def generate_all(data_path: Path = DATA_PATH) -> dict:
    """Full pipeline: load data → static charts → interactive charts."""
    print("\n========================================")
    print("  Lab 12 – Data Visualization Generator")
    print("========================================\n")

    df = load_data(data_path)
    print(f"Dataset: {len(df)} articles, {len(df.columns)} columns\n")

    print("── Static charts (matplotlib / seaborn) ──")
    static = run_static_charts(df)

    print("\n── Interactive charts (Plotly Express) ──")
    interactive = run_interactive_charts(df)

    print("\n========================================")
    print(f"  Done!  {len(static)} static + {len(interactive)} interactive")
    print(f"  Static  → {STATIC_OUT}")
    print(f"  Interactive → {INTERACTIVE_OUT}")
    print("========================================\n")

    return {"static": static, "interactive": interactive}