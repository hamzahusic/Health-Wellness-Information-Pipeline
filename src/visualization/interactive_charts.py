"""
Interactive visualization module for Health & Wellness Information Pipeline.
Uses Plotly Express (and Graph Objects for the multi-layout chart).
Lab 12 - Data Visualization
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

INTERACTIVE_OUT = Path("outputs/visualizations/interactive")
TEMPLATE = "plotly_white"


def _save_html(fig: go.Figure, stem: str,
               out_dir: Path = INTERACTIVE_OUT) -> str:
    """Write an interactive HTML file. Returns the file path as string."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stem}.html"
    fig.write_html(str(path))
    logger.info("Saved interactive chart: %s", path)
    return str(path)


# ── 1. Scatter – Content length over time by source ──────────────────────────
def interactive_content_length_scatter(df: pd.DataFrame,
                                       out_dir: Path = INTERACTIVE_OUT) -> str:
    """Interactive scatter: each article plotted by year and content length."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0).astype(int)
    data["author"] = data["author"].fillna("Unknown")

    fig = px.scatter(
        data,
        x="published_year",
        y="content_length",
        color="source_name",
        hover_name="title",
        hover_data={
            "author": True,
            "source_name": True,
            "published_year": True,
            "content_length": True,
        },
        labels={
            "published_year": "Publication Year",
            "content_length": "Content Length (chars)",
            "source_name": "Source",
        },
        title="Article Content Length Over Time – by Source",
        template=TEMPLATE,
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_layout(
        legend_title="Source",
        font=dict(family="Inter", size=13),
        height=580,
    )
    return _save_html(fig, "content_length_scatter_interactive", out_dir)


# ── 2. Bar – Top N sources by article count ──────────────────────────────────
def interactive_top_sources_bar(df: pd.DataFrame, n: int = 10,
                                out_dir: Path = INTERACTIVE_OUT) -> str:
    """Interactive horizontal bar: top-n sources by article count."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0)

    source_stats = (data.groupby("source_name")
                       .agg(
                           article_count=("title", "count"),
                           avg_content_length=("content_length", "mean"),
                           unique_authors=("author", "nunique"),
                       )
                       .reset_index()
                       .nlargest(n, "article_count")
                       .sort_values("article_count", ascending=True))
    source_stats["avg_content_length"] = source_stats["avg_content_length"].round(0).astype(int)

    fig = px.bar(
        source_stats,
        x="article_count",
        y="source_name",
        orientation="h",
        color="avg_content_length",
        color_continuous_scale="Viridis",
        hover_name="source_name",
        hover_data={
            "article_count": True,
            "avg_content_length": True,
            "unique_authors": True,
        },
        labels={
            "article_count": "Number of Articles",
            "source_name": "Source",
            "avg_content_length": "Avg Content Length (chars)",
        },
        title=f"Top {n} Sources by Article Count",
        template=TEMPLATE,
    )
    fig.update_layout(
        coloraxis_colorbar_title="Avg Length",
        font=dict(family="Inter", size=13),
        height=500,
    )
    return _save_html(fig, "top_sources_bar_interactive", out_dir)


# ── 3. Line – Articles published per year ────────────────────────────────────
def interactive_articles_per_year(df: pd.DataFrame,
                                  out_dir: Path = INTERACTIVE_OUT) -> str:
    """Interactive line: article count and avg content length per year."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0)

    yearly = (data.query("published_year >= 2000")
               .groupby("published_year")
               .agg(
                   article_count=("title", "count"),
                   avg_content_length=("content_length", "mean"),
                   unique_authors=("author", "nunique"),
                   unique_sources=("source_name", "nunique"),
               )
               .reset_index())
    yearly["avg_content_length"] = yearly["avg_content_length"].round(0).astype(int)

    fig = px.line(
        yearly,
        x="published_year",
        y="article_count",
        markers=True,
        hover_data={
            "avg_content_length": True,
            "unique_authors": True,
            "unique_sources": True,
            "article_count": True,
        },
        labels={
            "published_year": "Year",
            "article_count": "Number of Articles",
        },
        title="Health Articles Published per Year",
        template=TEMPLATE,
    )
    fig.update_traces(line_color="#1a6faf", line_width=2.5,
                      marker=dict(size=7))
    fig.update_layout(font=dict(family="Inter", size=13), height=450)
    return _save_html(fig, "articles_per_year_line", out_dir)


# ── 4. Box – Content length by source (interactive) ──────────────────────────
def interactive_source_content_boxplot(df: pd.DataFrame, top_n: int = 10,
                                       out_dir: Path = INTERACTIVE_OUT) -> str:
    """Interactive box plot: content length distribution per top source."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0).astype(int)
    data["author"] = data["author"].fillna("Unknown")

    top_sources = (data["source_name"].value_counts()
                   .head(top_n).index.tolist())
    data = data[data["source_name"].isin(top_sources)]

    order = (data.groupby("source_name")["content_length"]
               .median().sort_values(ascending=False).index.tolist())

    fig = px.box(
        data,
        x="source_name",
        y="content_length",
        category_orders={"source_name": order},
        color="source_name",
        hover_name="title",
        hover_data={"author": True, "published_year": True, "content_length": True},
        labels={
            "source_name": "Source",
            "content_length": "Content Length (chars)",
        },
        title=f"Content Length Distribution by Top {top_n} Sources",
        template=TEMPLATE,
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_layout(
        showlegend=False,
        font=dict(family="Inter", size=13),
        height=500,
    )
    return _save_html(fig, "source_content_boxplot_interactive", out_dir)


# ── 5. Multi-layout – 2×2 interactive dashboard ──────────────────────────────
def interactive_multi_layout(df: pd.DataFrame,
                              out_dir: Path = INTERACTIVE_OUT) -> str:
    """2×2 Plotly subplot combining sources, content length, volume, and authors."""
    data = df.copy()
    data["content_length"] = data["content"].str.len().fillna(0).astype(int)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Top 10 Sources by Article Count",
            "Content Length Distribution",
            "Articles per Year",
            "Top 10 Authors by Article Count",
        ),
        vertical_spacing=0.14,
        horizontal_spacing=0.10,
    )

    # Panel 1 – top 10 sources horizontal bar
    top_sources = (data["source_name"].dropna()
                   .value_counts()
                   .head(10)
                   .sort_values())
    fig.add_trace(
        go.Bar(
            x=top_sources.values,
            y=top_sources.index,
            orientation="h",
            marker_color="#1a6faf",
            name="Sources",
            hovertemplate="%{y}<br>%{x} articles<extra></extra>",
        ),
        row=1, col=1,
    )

    # Panel 2 – content length histogram
    fig.add_trace(
        go.Histogram(
            x=data["content_length"],
            nbinsx=25,
            marker_color="#2ca02c",
            name="Content Length",
            hovertemplate="Length: %{x}<br>Count: %{y}<extra></extra>",
        ),
        row=1, col=2,
    )

    # Panel 3 – articles per year bar
    yearly = (data.query("published_year >= 2000")
               .groupby("published_year")
               .size()
               .reset_index(name="article_count"))
    fig.add_trace(
        go.Bar(
            x=yearly["published_year"],
            y=yearly["article_count"],
            marker_color="#ff7f0e",
            name="Articles per Year",
            hovertemplate="Year: %{x}<br>Articles: %{y}<extra></extra>",
        ),
        row=2, col=1,
    )

    # Panel 4 – top 10 authors bar
    top_authors = (data["author"].dropna()
                   .value_counts()
                   .head(10)
                   .sort_values())
    fig.add_trace(
        go.Bar(
            x=top_authors.values,
            y=top_authors.index,
            orientation="h",
            marker_color="#9467bd",
            name="Authors",
            hovertemplate="%{y}<br>%{x} articles<extra></extra>",
        ),
        row=2, col=2,
    )

    fig.update_layout(
        title_text="Health & Wellness Articles Dashboard",
        title_font=dict(size=18),
        template=TEMPLATE,
        height=700,
        width=1100,
        showlegend=False,
        font=dict(family="Inter", size=11),
    )
    fig.update_xaxes(title_text="Number of Articles", row=1, col=1)
    fig.update_xaxes(title_text="Content Length (chars)", row=1, col=2)
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_xaxes(title_text="Number of Articles", row=2, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    fig.update_yaxes(title_text="Article Count", row=2, col=1)

    return _save_html(fig, "interactive_dashboard", out_dir)
