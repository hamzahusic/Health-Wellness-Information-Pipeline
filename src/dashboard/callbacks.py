"""
All Dash callbacks for the Health & Wellness Information Dashboard.
Three categories:
  1. Filter callbacks — update charts from dropdowns / sliders / search.
  2. Live callback   — update the ticker chart on every dcc.Interval tick.
"""
import collections
import random
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output

from .data_access import (
    COL_CATEGORY, COL_SOURCE, COL_WORD_COUNT, COL_YEAR,
    filter_articles, load_articles_df,
)

_DF = load_articles_df()

# Bounded circular buffer for the live ticker (last 60 ticks).
_LIVE_BUFFER = collections.deque(maxlen=60)

DARK_TEMPLATE = "plotly_dark"
CHART_BG = "#112236"
_MARGIN = dict(l=10, r=10, t=10, b=10)


def register_callbacks(app):
    """Register all callbacks on the given Dash app instance."""

    # ── Callback 1: Top sources bar chart ────────────────────────────
    @app.callback(
        Output("revenue-chart", "figure"),
        Input("genre-filter", "value"),
        Input("year-slider", "value"),
        Input("search-input", "value"),
    )
    def update_sources_chart(category, year_range, search):
        df = filter_articles(_DF, category or None, tuple(year_range) if year_range else None, search)

        if COL_SOURCE not in df.columns or df.empty:
            return _empty_figure("Source data not available.")

        top10 = (
            df.groupby(COL_SOURCE)
            .size()
            .nlargest(10)
            .reset_index(name="count")
        )
        if top10.empty:
            return _empty_figure("No articles match the current filters.")

        fig = px.bar(
            top10,
            x="count",
            y=COL_SOURCE,
            orientation="h",
            text="count",
            color="count",
            color_continuous_scale="Blues",
            template=DARK_TEMPLATE,
            labels={"count": "Article Count", COL_SOURCE: ""},
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            paper_bgcolor=CHART_BG,
            plot_bgcolor=CHART_BG,
            coloraxis_showscale=False,
            margin=_MARGIN,
            yaxis={"categoryorder": "total ascending"},
        )
        return fig

    # ── Callback 2: Article count by category ────────────────────────
    @app.callback(
        Output("rating-chart", "figure"),
        Input("genre-filter", "value"),
        Input("year-slider", "value"),
        Input("search-input", "value"),
    )
    def update_category_chart(category, year_range, search):
        df = filter_articles(_DF, category or None, tuple(year_range) if year_range else None, search)

        if COL_CATEGORY not in df.columns or df.empty:
            return _empty_figure("Category data not available.")

        counts = df[COL_CATEGORY].dropna().value_counts().reset_index()
        counts.columns = [COL_CATEGORY, "count"]

        fig = px.bar(
            counts,
            x=COL_CATEGORY,
            y="count",
            color=COL_CATEGORY,
            template=DARK_TEMPLATE,
            labels={"count": "Article Count", COL_CATEGORY: "Category"},
        )
        fig.update_layout(
            paper_bgcolor=CHART_BG,
            plot_bgcolor=CHART_BG,
            showlegend=False,
            margin=_MARGIN,
        )
        return fig

    # ── Callback 3: Word count distribution by category ───────────────
    @app.callback(
        Output("scatter-chart", "figure"),
        Input("genre-filter", "value"),
        Input("year-slider", "value"),
        Input("search-input", "value"),
    )
    def update_wordcount_chart(category, year_range, search):
        df = filter_articles(_DF, category or None, tuple(year_range) if year_range else None, search)

        if COL_WORD_COUNT not in df.columns or df.empty:
            return _empty_figure("Word count data not available.")

        plot_df = df.copy()
        plot_df[COL_WORD_COUNT] = pd.to_numeric(plot_df[COL_WORD_COUNT], errors="coerce")
        plot_df = plot_df[plot_df[COL_WORD_COUNT] > 0].dropna(subset=[COL_WORD_COUNT])

        if plot_df.empty:
            return _empty_figure("No valid word count data.")

        if COL_CATEGORY in plot_df.columns:
            fig = px.box(
                plot_df,
                x=COL_CATEGORY,
                y=COL_WORD_COUNT,
                color=COL_CATEGORY,
                template=DARK_TEMPLATE,
                labels={COL_WORD_COUNT: "Word Count", COL_CATEGORY: ""},
            )
        else:
            fig = px.histogram(plot_df, x=COL_WORD_COUNT, nbins=30, template=DARK_TEMPLATE)

        fig.update_layout(
            paper_bgcolor=CHART_BG,
            plot_bgcolor=CHART_BG,
            showlegend=False,
            margin=_MARGIN,
        )
        return fig

    # ── Callback 4: Articles published per year ───────────────────────
    @app.callback(
        Output("trend-chart", "figure"),
        Input("genre-filter", "value"),
        Input("year-slider", "value"),
        Input("search-input", "value"),
    )
    def update_trend_chart(category, year_range, search):
        df = filter_articles(_DF, category or None, tuple(year_range) if year_range else None, search)

        if COL_YEAR not in df.columns or df.empty:
            return _empty_figure("Year data not available.")

        df = df.copy()
        df[COL_YEAR] = pd.to_numeric(df[COL_YEAR], errors="coerce")
        counts = df.groupby(COL_YEAR).size().reset_index(name="count")
        fig = px.line(
            counts,
            x=COL_YEAR,
            y="count",
            markers=True,
            template=DARK_TEMPLATE,
            labels={COL_YEAR: "Year", "count": "Articles Published"},
        )
        fig.update_traces(line_color="#4a9eff", marker_color="#34d399")
        fig.update_layout(paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG, margin=_MARGIN)
        return fig

    # ── Callback 5: Live ingestion ticker ────────────────────────────
    @app.callback(
        Output("live-chart", "figure"),
        Input("live-interval", "n_intervals"),
    )
    def update_live_chart(n):
        """
        Simulates a live article ingestion stream by appending a new point
        on every dcc.Interval tick (every 3 seconds).

        In production this would read from a message queue (e.g. Kafka) or
        a time-series database. Here random.gauss() simulates a fluctuating
        ingestion rate.

        collections.deque(maxlen=60) keeps memory bounded: new points
        automatically push out the oldest ones.
        """
        _LIVE_BUFFER.append({
            "tick": n,
            "value": 50 + random.gauss(0, 5) + 0.3 * (n % 20),
            "ts": time.strftime("%H:%M:%S"),
        })

        ticks = [p["tick"] for p in _LIVE_BUFFER]
        values = [p["value"] for p in _LIVE_BUFFER]
        labels = [p["ts"] for p in _LIVE_BUFFER]

        fig = go.Figure(
            go.Scatter(
                x=ticks,
                y=values,
                mode="lines+markers",
                line=dict(color="#34d399", width=2),
                marker=dict(size=4, color="#34d399"),
                hovertext=labels,
                hoverinfo="text+y",
                fill="tozeroy",
                fillcolor="rgba(52,211,153,0.1)",
            )
        )
        fig.update_layout(
            template=DARK_TEMPLATE,
            paper_bgcolor=CHART_BG,
            plot_bgcolor=CHART_BG,
            xaxis_title="Tick",
            yaxis_title="Simulated Articles / sec",
            margin=_MARGIN,
            height=200,
        )
        return fig


# ─────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────

def _empty_figure(message: str) -> go.Figure:
    """Return a blank dark figure with a centred annotation."""
    fig = go.Figure()
    fig.update_layout(
        template=DARK_TEMPLATE,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        annotations=[dict(
            text=message, showarrow=False,
            xref="paper", yref="paper",
            x=0.5, y=0.5, font=dict(color="#8899aa"),
        )],
    )
    return fig
