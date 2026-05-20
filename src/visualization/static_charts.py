"""
Static visualization module for Health & Wellness Information Pipeline.
Uses matplotlib (object-oriented API) and seaborn for all static charts.
Lab 12 - Data Visualization
"""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend so saving works outside notebooks
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Global style ──────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid")
sns.set_context("notebook")
sns.set_palette("viridis")

STATIC_OUT = Path("outputs/visualizations/static")


def _save(fig: plt.Figure, stem: str, out_dir: Path = STATIC_OUT) -> dict:
    """Save figure as PNG (300 dpi) and PDF. Returns dict of saved paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / f"{stem}.png"
    pdf_path = out_dir / f"{stem}.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s  (PNG + PDF)", stem)
    return {"png": str(png_path), "pdf": str(pdf_path)}


# ── 1. Bar chart – Top N sources by article count ────────────────────────────
def plot_top_sources_by_count(df: pd.DataFrame, n: int = 10,
                              out_dir: Path = STATIC_OUT) -> dict:
    """Horizontal bar chart: top-n news sources by article count."""
    counts = (df["source_name"].dropna()
               .value_counts()
               .head(n)
               .sort_values())

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("viridis", n)
    bars = ax.barh(counts.index, counts.values, color=colors)

    for bar in bars:
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                str(int(bar.get_width())), va="center", fontsize=9)

    ax.set_xlabel("Number of Articles", fontsize=11)
    ax.set_title(f"Top {n} Sources by Article Count", fontsize=14, fontweight="bold")
    ax.set_xlim(0, counts.max() * 1.15)
    fig.tight_layout()

    return _save(fig, "top_sources_by_count", out_dir)


# ── 2. Line chart – Article publication volume over years ────────────────────
def plot_articles_over_years(df: pd.DataFrame,
                             out_dir: Path = STATIC_OUT) -> dict:
    """Line chart: article count and avg content length per publish year."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0)

    yearly = (data.groupby("published_year")
               .agg(article_count=("title", "count"),
                    avg_content_length=("content_length", "mean"))
               .reset_index()
               .query("published_year >= 2000"))

    fig, ax1 = plt.subplots(figsize=(12, 5))
    color_bar = "#a8d5e2"
    color_line = "#1a6faf"

    ax1.bar(yearly["published_year"], yearly["article_count"],
            color=color_bar, alpha=0.5, label="Article Count")
    ax1.set_ylabel("Number of Articles", color=color_bar, fontsize=11)
    ax1.tick_params(axis="y", labelcolor=color_bar)

    ax2 = ax1.twinx()
    ax2.plot(yearly["published_year"], yearly["avg_content_length"],
             color=color_line, linewidth=2.5, marker="o", markersize=5,
             label="Avg. Content Length")
    ax2.set_ylabel("Avg. Content Length (chars)", color=color_line, fontsize=11)
    ax2.tick_params(axis="y", labelcolor=color_line)

    ax1.set_xlabel("Publication Year", fontsize=11)
    ax1.set_title("Health Article Volume and Avg. Content Length Over the Years",
                  fontsize=14, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    fig.tight_layout()
    return _save(fig, "articles_over_years", out_dir)


# ── 3. Scatter plot – Source article count vs avg content length ──────────────
def plot_source_count_vs_length(df: pd.DataFrame,
                                out_dir: Path = STATIC_OUT) -> dict:
    """Scatter: per-source article count vs avg content length."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0)

    source_stats = (data.groupby("source_name")
                       .agg(article_count=("title", "count"),
                            avg_length=("content_length", "mean"))
                       .reset_index())

    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(source_stats["article_count"],
                         source_stats["avg_length"] / 1000,
                         c=source_stats["article_count"],
                         cmap="viridis", alpha=0.8, s=80, edgecolors="white")

    for _, row in source_stats.iterrows():
        ax.annotate(row["source_name"],
                    (row["article_count"], row["avg_length"] / 1000),
                    textcoords="offset points", xytext=(5, 5), fontsize=7, alpha=0.85)

    plt.colorbar(scatter, ax=ax, label="Article Count")
    ax.set_xlabel("Number of Articles", fontsize=11)
    ax.set_ylabel("Avg. Content Length (thousand chars)", fontsize=11)
    ax.set_title("Source Productivity: Article Count vs Avg. Content Length",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()

    return _save(fig, "source_count_vs_length", out_dir)


# ── 4. Histogram – Distribution of article content length ────────────────────
def plot_content_length_distribution(df: pd.DataFrame,
                                     out_dir: Path = STATIC_OUT) -> dict:
    """Histogram + KDE of article content length."""
    lengths = df["content"].str.len().dropna()

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(lengths / 1000, bins=25, kde=True,
                 color="#1a6faf", edgecolor="white", ax=ax)
    ax.axvline(lengths.mean() / 1000, color="firebrick",
               linestyle="--", linewidth=1.8,
               label=f"Mean = {lengths.mean() / 1000:.1f}K chars")
    ax.axvline(lengths.median() / 1000, color="darkorange",
               linestyle="-.", linewidth=1.8,
               label=f"Median = {lengths.median() / 1000:.1f}K chars")
    ax.set_xlabel("Content Length (thousand chars)", fontsize=11)
    ax.set_ylabel("Number of Articles", fontsize=11)
    ax.set_title("Distribution of Article Content Lengths", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    fig.tight_layout()

    return _save(fig, "content_length_distribution", out_dir)


# ── 5. Box plot – Content length by top sources ──────────────────────────────
def plot_content_length_by_source(df: pd.DataFrame, top_n: int = 10,
                                  out_dir: Path = STATIC_OUT) -> dict:
    """Box-and-whisker plot: content length distribution per top source."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0)

    top_sources = (data["source_name"].value_counts()
                   .head(top_n).index.tolist())
    data = data[data["source_name"].isin(top_sources)]

    order = (data.groupby("source_name")["content_length"]
               .median().sort_values(ascending=False).index.tolist())

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=data, x="source_name", y="content_length",
                order=order, hue="source_name", palette="viridis",
                legend=False, ax=ax)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
    ax.set_xlabel("Source", fontsize=11)
    ax.set_ylabel("Content Length (chars)", fontsize=11)
    ax.set_title(f"Content Length Distribution by Top {top_n} Sources",
                 fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()

    return _save(fig, "content_length_by_source", out_dir)


# ── 6. Heatmap – Article count by source × year ──────────────────────────────
def plot_source_year_heatmap(df: pd.DataFrame,
                             out_dir: Path = STATIC_OUT) -> dict:
    """Heatmap: article count per source (rows) × published year (columns)."""
    top_sources = (df["source_name"].value_counts()
                   .head(12).index.tolist())
    data = df[df["source_name"].isin(top_sources)]

    pivot = (data.groupby(["source_name", "published_year"])
               .size()
               .unstack(fill_value=0))

    fig, ax = plt.subplots(figsize=(max(8, len(pivot.columns) * 0.9), 7))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="YlOrRd",
                linewidths=0.4, ax=ax, annot_kws={"size": 9})
    ax.set_title("Article Count by Source and Publication Year",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Publication Year", fontsize=11)
    ax.set_ylabel("Source", fontsize=11)
    ax.tick_params(axis="y", rotation=0)
    fig.tight_layout()

    return _save(fig, "source_year_heatmap", out_dir)


# ── 7. Bar chart – Top N authors by article count ────────────────────────────
def plot_top_authors_by_count(df: pd.DataFrame, n: int = 10,
                              out_dir: Path = STATIC_OUT) -> dict:
    """Vertical bar chart: number of articles per top author."""
    counts = (df["author"].dropna()
               .value_counts()
               .head(n))

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(counts.index, counts.values,
                  color=sns.color_palette("viridis", len(counts)))
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                str(int(bar.get_height())), ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Author", fontsize=11)
    ax.set_ylabel("Number of Articles", fontsize=11)
    ax.set_title(f"Top {n} Authors by Article Count", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()

    return _save(fig, "top_authors_by_count", out_dir)


# ── 8. Subplot layout – 2×2 dashboard ────────────────────────────────────────
def plot_dashboard_subplots(df: pd.DataFrame,
                            out_dir: Path = STATIC_OUT) -> dict:
    """2×2 multi-panel figure combining four key health article charts."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Health & Wellness Articles Dashboard", fontsize=16,
                 fontweight="bold", y=1.01)

    # Panel A: top 10 sources by article count
    counts = (data["source_name"].dropna()
               .value_counts()
               .head(10)
               .sort_values())
    axes[0, 0].barh(counts.index, counts.values,
                    color=sns.color_palette("viridis", 10))
    axes[0, 0].set_title("Top 10 Sources by Article Count", fontsize=11, fontweight="bold")
    axes[0, 0].set_xlabel("Number of Articles")

    # Panel B: content length distribution
    sns.histplot(data["content_length"].dropna() / 1000, bins=20, kde=True,
                 color="#1a6faf", ax=axes[0, 1])
    axes[0, 1].set_title("Content Length Distribution", fontsize=11, fontweight="bold")
    axes[0, 1].set_xlabel("Content Length (thousand chars)")
    axes[0, 1].set_ylabel("Count")

    # Panel C: article volume over years
    yearly = (data.groupby("published_year")
               .size()
               .reset_index(name="article_count")
               .query("published_year >= 2000"))
    axes[1, 0].bar(yearly["published_year"], yearly["article_count"],
                   color=sns.color_palette("viridis", len(yearly)))
    axes[1, 0].set_title("Article Volume Over Years", fontsize=11, fontweight="bold")
    axes[1, 0].set_xlabel("Year")
    axes[1, 0].set_ylabel("Count")

    # Panel D: top 8 authors
    author_counts = (data["author"].dropna()
                      .value_counts()
                      .head(8))
    axes[1, 1].bar(author_counts.index, author_counts.values,
                   color=sns.color_palette("viridis", len(author_counts)))
    axes[1, 1].set_title("Top 8 Authors by Article Count", fontsize=11, fontweight="bold")
    axes[1, 1].set_xlabel("Author")
    axes[1, 1].set_ylabel("Count")
    axes[1, 1].tick_params(axis="x", rotation=30)

    fig.tight_layout()
    return _save(fig, "dashboard_subplots", out_dir)
