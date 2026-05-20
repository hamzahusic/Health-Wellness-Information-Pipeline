#!/usr/bin/env python3
"""
generate_visualizations.py
==========================
Lab 12 – Data Visualization entry-point script.

Usage (from the project root):
    python scripts/generate_visualizations.py
    python scripts/generate_visualizations.py --data path/to/articles_clean.csv

The script:
  1. Loads the cleaned articles dataset (data/processed/cleaned/articles_clean.csv)
  2. Generates 8 static charts (matplotlib + seaborn) → outputs/visualizations/static/
  3. Generates 5 interactive charts (Plotly Express)  → outputs/visualizations/interactive/

Each static chart is saved as both PNG (300 dpi) and PDF.
Each interactive chart is saved as a self-contained HTML file.
"""

import argparse
import logging
import sys
from pathlib import Path

# ── resolve project root so modules are importable regardless of CWD ─────────
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main():
    parser = argparse.ArgumentParser(
        description="Lab 12 – Health & Wellness Data Visualization Generator"
    )
    parser.add_argument(
        "--data",
        default=str(ROOT / "data" / "processed" / "cleaned" / "articles_clean.csv"),
        help="Path to the cleaned articles CSV (default: data/processed/cleaned/articles_clean.csv)",
    )
    args = parser.parse_args()

    # Change working directory to project root so relative output paths work
    import os
    os.chdir(ROOT)

    from visualization.chart_generator import generate_all

    generate_all(data_path=Path(args.data))


if __name__ == "__main__":
    main()