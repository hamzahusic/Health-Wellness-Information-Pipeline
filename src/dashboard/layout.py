"""
Page layout for the Health & Wellness Information Dashboard.
Uses dash-bootstrap-components for the responsive grid.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html

from .data_access import (
    COL_CATEGORY, COL_SOURCE, COL_WORD_COUNT,
    get_categories, get_years, load_articles_df,
)

_df = load_articles_df()
_categories = get_categories(_df)
_year_min, _year_max = get_years(_df)

CATEGORY_OPTIONS = [{"label": c, "value": c} for c in _categories]


def create_layout() -> dbc.Container:
    """Return the full page layout as a Bootstrap Container."""
    return dbc.Container(
        fluid=True,
        style={"backgroundColor": "#0a1628", "minHeight": "100vh", "padding": "20px"},
        children=[
            # ── Header ───────────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    html.Div([
                        html.H1(
                            "Health & Wellness Information Dashboard",
                            style={"color": "#ffffff", "fontWeight": "700", "marginBottom": "4px"},
                        ),
                        html.P(
                            "Interactive exploration of the Health & Wellness Information Pipeline",
                            style={"color": "#8899aa", "fontSize": "14px"},
                        ),
                    ]),
                    width=12,
                ),
                className="mb-4",
            ),

            # ── KPI Cards ────────────────────────────────────────────
            dbc.Row(
                id="kpi-row",
                children=_build_kpi_cards(_df),
                className="mb-4",
            ),

            # ── Filter Bar ───────────────────────────────────────────
            dbc.Row([
                dbc.Col([
                    html.Label("Category", style={"color": "#8899aa", "fontSize": "12px"}),
                    dcc.Dropdown(
                        id="genre-filter",
                        options=[{"label": "All Categories", "value": ""}] + CATEGORY_OPTIONS,
                        value="",
                        clearable=False,
                        style={"backgroundColor": "#1a2840", "color": "#000"},
                    ),
                ], width=3),

                dbc.Col([
                    html.Label("Year Range", style={"color": "#8899aa", "fontSize": "12px"}),
                    dcc.RangeSlider(
                        id="year-slider",
                        min=_year_min,
                        max=_year_max,
                        step=1,
                        value=[_year_min, _year_max],
                        marks={
                            y: {"label": str(y), "style": {"color": "#8899aa"}}
                            for y in range(_year_min, _year_max + 1, 1)
                        },
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ], width=5),

                dbc.Col([
                    html.Label("Search Articles", style={"color": "#8899aa", "fontSize": "12px"}),
                    dcc.Input(
                        id="search-input",
                        type="text",
                        placeholder="Type an article title...",
                        debounce=True,
                        style={
                            "width": "100%", "padding": "8px",
                            "backgroundColor": "#1a2840",
                            "border": "1px solid #2a3850",
                            "color": "#ffffff", "borderRadius": "4px",
                        },
                    ),
                ], width=4),
            ], className="mb-4", style={
                "backgroundColor": "#112236", "padding": "16px", "borderRadius": "8px",
            }),

            # ── Main Charts Row ───────────────────────────────────────
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(
                            "Top 10 Sources by Article Count",
                            style={"backgroundColor": "#112236", "color": "#ffffff"},
                        ),
                        dbc.CardBody(dcc.Graph(id="revenue-chart", config={"displayModeBar": False})),
                    ], style={"backgroundColor": "#112236", "border": "1px solid #1e3a5f"}),
                    width=6,
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(
                            "Article Count by Category",
                            style={"backgroundColor": "#112236", "color": "#ffffff"},
                        ),
                        dbc.CardBody(dcc.Graph(id="rating-chart", config={"displayModeBar": False})),
                    ], style={"backgroundColor": "#112236", "border": "1px solid #1e3a5f"}),
                    width=6,
                ),
            ], className="mb-4"),

            # ── Second Charts Row ─────────────────────────────────────
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(
                            "Word Count Distribution by Category",
                            style={"backgroundColor": "#112236", "color": "#ffffff"},
                        ),
                        dbc.CardBody(dcc.Graph(id="scatter-chart", config={"displayModeBar": False})),
                    ], style={"backgroundColor": "#112236", "border": "1px solid #1e3a5f"}),
                    width=6,
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(
                            "Articles Published per Year",
                            style={"backgroundColor": "#112236", "color": "#ffffff"},
                        ),
                        dbc.CardBody(dcc.Graph(id="trend-chart", config={"displayModeBar": False})),
                    ], style={"backgroundColor": "#112236", "border": "1px solid #1e3a5f"}),
                    width=6,
                ),
            ], className="mb-4"),

            # ── Live Ticker ───────────────────────────────────────────
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(
                            "Live Ingestion Rate (simulated stream)",
                            style={"backgroundColor": "#112236", "color": "#ffffff"},
                        ),
                        dbc.CardBody([
                            dcc.Graph(id="live-chart", config={"displayModeBar": False}),
                            dcc.Interval(
                                id="live-interval",
                                interval=3000,
                                n_intervals=0,
                            ),
                        ]),
                    ], style={"backgroundColor": "#112236", "border": "1px solid #1e3a5f"}),
                    width=12,
                ),
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────

def _build_kpi_cards(df) -> list:
    """Return four KPI metric cards for the header row."""
    import pandas as pd

    total = len(df)
    avg_words = (
        pd.to_numeric(df[COL_WORD_COUNT], errors="coerce").mean()
        if COL_WORD_COUNT in df.columns else 0
    )
    sources_n = df[COL_SOURCE].nunique() if COL_SOURCE in df.columns else 0
    cats_n = df[COL_CATEGORY].nunique() if COL_CATEGORY in df.columns else 0

    cards = [
        ("Total Articles", f"{total:,}", "#4a9eff"),
        ("Avg Word Count", f"{avg_words:.0f}", "#34d399"),
        ("Unique Sources", str(sources_n), "#f59e0b"),
        ("Categories", str(cats_n), "#a78bfa"),
    ]

    return [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5(label, style={"color": "#8899aa", "fontSize": "13px", "marginBottom": "4px"}),
                    html.H2(value, style={"color": color, "fontWeight": "700", "marginBottom": "0"}),
                ]),
                style={"backgroundColor": "#112236", "border": f"1px solid {color}"},
            ),
            width=3,
        )
        for label, value, color in cards
    ]
