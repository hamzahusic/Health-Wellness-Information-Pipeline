import sys
import os
import logging
import pandas as pd
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cleaning.clean_pipeline import run_cleaning_pipeline

logger = logging.getLogger(__name__)

def run_visualizations_pipeline(cleaned_path=None):
    """Lab 12 – generate all static and interactive visualizations."""
    logging.info("--- Lab 12 Visualization Pipeline Starting ---")
    if cleaned_path is None:
        BASE_DIR = Path(__file__).resolve().parents[2]
        cleaned_path = BASE_DIR / "data" / "processed" / "cleaned" / "articles_clean.csv"

    try:
        import sys
        BASE_DIR = Path(__file__).resolve().parents[2]
        if str(BASE_DIR / "src") not in sys.path:
            sys.path.insert(0, str(BASE_DIR / "src"))
        import os
        os.chdir(BASE_DIR)
        from visualization.chart_generator import generate_all
        results = generate_all(data_path=Path(cleaned_path))
        logging.info(
            "Visualization pipeline complete: %d static, %d interactive",
            len(results.get("static", {})),
            len(results.get("interactive", {})),
        )
        return results
    except Exception as e:
        logging.error("Visualization pipeline failed: %s", e)
        raise

def run_analytics_pipeline(cleaned_path, mysql_password=""):
    """Run the full analytics step."""
    from analytics.db_connector import get_connection, populate_articles, query_articles
    from analytics.data_combiner import merge_mysql_mongodb
    from analytics.aggregator import source_summary, yearly_trends
    from analytics.time_series import parse_published_dates, build_monthly_series, resample_series
    from analytics.pivot_builder import articles_per_source_year
    from analytics.mongo_pipeline import build_source_pipeline, run_pipeline as run_mongo_pipeline
    from analytics.insight_reporter import run_all_questions
    from pymongo import MongoClient

    logger.info("--- Lab 10 Analytics Pipeline Starting ---")
    os.makedirs("../../data/processed/analytics", exist_ok=True)

    df = pd.read_csv(cleaned_path)
    logger.info("Loaded cleaned data: %d rows", len(df))

    if "content" in df.columns:
        df["content_length"] = df["content"].str.len().fillna(0).astype(int)

    # MySQL: create table, populate and query
    try:
        conn = get_connection(password=mysql_password, database="health_pipeline")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_articles (
                id          INT AUTO_INCREMENT PRIMARY KEY,
                source_id   VARCHAR(255),
                title       VARCHAR(500) NOT NULL,
                source_name VARCHAR(255),
                author      VARCHAR(255),
                publishedAt DATETIME,
                description TEXT,
                content     MEDIUMTEXT,
                url         VARCHAR(2083),
                publish_year SMALLINT,
                UNIQUE KEY  idx_url (url(500)),
                INDEX idx_source_name (source_name),
                INDEX idx_publish_year (publish_year)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        conn.commit()
        cursor.execute("DELETE FROM health_articles")
        conn.commit()
        cursor.close()
        populate_articles(conn, df)
        mysql_df = query_articles(conn)
        logger.info("MySQL step complete: %d rows", len(mysql_df))
    except Exception as e:
        logger.warning("MySQL step skipped: %s", e)
        cols = [c for c in ["title", "source_name", "author", "publish_year"] if c in df.columns]
        mysql_df = df[cols].copy() if cols else pd.DataFrame()

    # Parse dates
    if "publishedAt" in df.columns:
        df = parse_published_dates(df, date_col="publishedAt")

    # Merge with MySQL if available
    merge_key = None
    mongo_cols = ["url", "title", "source_name", "author", "publishedAt", "content", "description"]
    mongo_df = df[[c for c in mongo_cols if c in df.columns]].copy()
    for candidate in ["url", "title", "source_id"]:
        if candidate in mysql_df.columns and candidate in mongo_df.columns:
            merge_key = candidate
            break
    if merge_key and not mysql_df.empty:
        df = merge_mysql_mongodb(mysql_df, mongo_df, on=merge_key, how="inner")
        for col in ["title", "source_name", "author", "publishedAt"]:
            if f"{col}_mysql" in df.columns:
                df[col] = df[f"{col}_mysql"].fillna(df.get(f"{col}_mongo", ""))

    # Source summary
    src_df = source_summary(df)
    src_df.to_csv("../../data/processed/analytics/source_analysis.csv", index=False)
    logger.info("Source summary: %d sources", len(src_df))

    # Yearly trends
    yearly_df = yearly_trends(df)
    yearly_df.to_csv("../../data/processed/analytics/yearly_trends.csv", index=False)
    logger.info("Yearly trends saved")

    # Pivot table
    try:
        pt = articles_per_source_year(df)
        pt.to_csv("../../data/processed/analytics/pivot_source_year.csv")
        logger.info("Pivot table saved")
    except Exception as e:
        logger.warning("Pivot table skipped: %s", e)

    # Time series
    monthly = build_monthly_series(df, date_col="publishedAt")
    yearly_ts = resample_series(monthly, freq="YE", agg="sum")
    logger.info("Monthly series: %d periods", len(monthly))
    logger.info("Yearly totals:\n%s", yearly_ts.tail(5))

    # MongoDB aggregation pipeline
    try:
        client = MongoClient("mongodb://localhost:27017/")
        collection = client["articles_pipeline"]["raw_articles"]
        pipeline = build_source_pipeline(min_article_count=5, top_n=10)
        mongo_result = run_mongo_pipeline(collection, pipeline)
        logger.info("MongoDB pipeline: %d sources", len(mongo_result))
    except Exception as e:
        logger.warning("MongoDB pipeline skipped: %s", e)

    # Analytical questions
    df_analysis = df.copy()
    if "content" in df_analysis.columns and "content_length" not in df_analysis.columns:
        df_analysis["content_length"] = df_analysis["content"].str.len().fillna(0).astype(int)
    run_all_questions(df_analysis)

    logger.info("--- Lab 10 Analytics Pipeline Complete ---")
    return df
 


def run_cleaning():

    logging.info('=== Lab 9: Data Cleaning ===')

    raw_csv = Path('../../data/processed/analytics/articles.csv')
    if not raw_csv.exists():
        logging.warning('articles.csv not found at %s', raw_csv)
        return None

    df_raw = pd.read_csv(raw_csv, low_memory=False)
    logging.info('Loaded %d rows from %s', len(df_raw), raw_csv)

    df_clean = run_cleaning_pipeline(df_raw, save=True)
    logging.info('Cleaning complete: %d rows saved to ../../data/processed/cleaned/', len(df_clean))
    return df_clean


def run_analytics():
    import numpy as np
    from analytics.quality_report import full_quality_report, outlier_report, save_missing_heatmap
    from analytics.data_loader import chunked_stats, load_from_mongodb, memory_comparison, save_to_csv, optimise_dtypes
    from analytics.numpy_ops import demonstrate_array_creation, vectorized_operations
    from analytics.explorer import extract_publish_year, inspect_shape, plot_distributions, value_counts_report, print_info, describe_numeric
    from analytics.selector import boolean_filter, isin_filter, loc_filter
    from analytics.regex_ops import health_keyword_count, top_health_keywords, normalize_author

    PROCESSED_DIR = Path("../../data/processed/analytics")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    CSV_PATH     = str(PROCESSED_DIR / "articles.csv")
    OPT_CSV_PATH = str(PROCESSED_DIR / "articles_optimised.csv")

    # ── Part A: NumPy ─────────────────────────
    arrays = demonstrate_array_creation()
    logger.info("NumPy arrays created: %s", list(arrays.keys()))

    content_lengths = np.array([320, 850, 1200, 95, 640, 480, 2100, 760])
    word_counts     = np.array([58, 143, 210, 17, 112, 84, 380, 134])

    results = vectorized_operations(content_lengths, word_counts)
    logger.info(
        "Vectorized ops: mean_length=%.2f long_articles=%d",
        results["stats"]["mean"],
        results["high_rated"].sum()
    )

    # ── Part B: Data Loader ───────────────────
    df_articles = load_from_mongodb()

    if df_articles is None or df_articles.empty:
        logging.warning("MongoDB returned empty dataset — skipping analytics")
        return

    if 'data' in df_articles.columns:
        df_articles = pd.json_normalize(df_articles['data'])
    save_to_csv(df_articles, CSV_PATH)

    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        raise ValueError(f"CSV file is empty or missing: {CSV_PATH}")

    chunk_results = chunked_stats(CSV_PATH)
    logger.info(
        "Chunked stats: mean_content_length=%.1f over %d rows",
        chunk_results["mean_content_length"],
        chunk_results["total_rows"]
    )
    logger.info("Top sources:\n%s", chunk_results["source_df"].head())
    logger.info("Top authors:\n%s", chunk_results["author_df"].head())

    df_opt = optimise_dtypes(df_articles)
    mem = memory_comparison(df_articles, df_opt)
    logger.info("Memory reduction: %.1f%%", mem["reduction_pct"])

    save_to_csv(df_opt, OPT_CSV_PATH)

    # ── Part C: Explore ───────────────────────
    shape_info = inspect_shape(df_articles)
    logger.info("Dataset shape: %dx%d", shape_info["rows"], shape_info["columns"])

    print_info(df_articles)

    numeric_summary = describe_numeric(df_articles)
    logger.info("Numeric summary:\n%s", numeric_summary.to_string())

    vc = value_counts_report(df_articles)
    for col, data in vc.items():
        logger.info("%s: %d unique values", col, data["nunique"])

    df_articles = extract_publish_year(df_articles)
    plot_distributions(df_articles, str(PROCESSED_DIR / "distributions.png"))

    substantial = loc_filter(df_articles, min_content_len=200)
    logger.info("Articles with substantial content: %d", len(substantial))

    quality_articles = boolean_filter(df_articles)
    logger.info("Articles with content + author + title: %d", len(quality_articles))

    # ── Part D: Regex & Quality ───────────────
    if 'author' in df_articles.columns:
        df_articles['author'] = normalize_author(df_articles['author'])

    logger.info("Health keyword matches: %d articles", health_keyword_count(df_articles))
    logger.info("Top health keywords: %s", top_health_keywords(df_articles, n=10))

    quality_df = full_quality_report(df_articles)
    quality_df.to_csv(str(PROCESSED_DIR / "data_quality_report.csv"), index=False)

    save_missing_heatmap(df_articles, str(PROCESSED_DIR / "missing_heatmap.png"))

    outliers = outlier_report(df_articles)
    logger.info("Outlier report columns: %d", len(outliers))

    logger.info("COMPLETED")


def run_audio_video_stage():
    from storage.mongo import get_db, save_transcript
    from audio_processing.loader import inspect_audio, load_audio
    from audio_processing.processor import trim_audio, apply_fades, export_audio
    from audio_processing.transcriber import (
        transcribe_audio, save_transcript_json,
        save_transcript_txt, save_transcript_srt
    )
    from video_processing.loader import inspect_video, extract_audio_from_video
    from video_processing.frame_extractor import extract_keyframes

    logging.info('=== Audio/Video Processing Stage ===')
    db = get_db()

    # AUDIO
    for audio_file in Path('data/raw/audio').glob('*.mp3'):
        try:
            logging.info(f'Processing audio: {audio_file.name}')

            audio = load_audio(str(audio_file))
            trimmed = trim_audio(audio, 0, min(30000, len(audio)))
            faded = apply_fades(trimmed)

            export_audio(faded, f'data/processed/audio/{audio_file.stem}_clip.mp3')

            result = transcribe_audio(str(audio_file))

            j = f'data/processed/transcripts/{audio_file.stem}.json'
            t = f'data/processed/transcripts/{audio_file.stem}.txt'
            s = f'data/processed/transcripts/{audio_file.stem}.srt'

            save_transcript_json(result, j)
            save_transcript_txt(result, t)
            save_transcript_srt(result, s)
            save_transcript(db, result, str(audio_file), 'audio', json_path=j, txt_path=t, srt_path=s)

        except Exception as e:
            logging.error(f'Audio error: {e}')

    # VIDEO
    for video_file in Path('../../data/raw/video').glob('*.mp4'):
        try:
            logging.info(f'Processing video: {video_file.name}')

            extract_keyframes(str(video_file), f'../../data/processed/frames/{video_file.stem}/')

            audio_out = f'../../data/processed/audio/{video_file.stem}.mp3'
            extract_audio_from_video(str(video_file), audio_out)

            result = transcribe_audio(audio_out)

            j = f'../../data/processed/transcripts/{video_file.stem}.json'
            t = f'../../data/processed/transcripts/{video_file.stem}.txt'
            s = f'../../data/processed/transcripts/{video_file.stem}.srt'

            save_transcript_json(result, j)
            save_transcript_txt(result, t)
            save_transcript_srt(result, s)
            save_transcript(db, result, str(video_file), 'video', json_path=j, txt_path=t, srt_path=s)

        except Exception as e:
            logging.error(f'Video error: {e}')

    logging.info('=== Audio/Video Processing Stage Complete ===')

def run_embeddings_pipeline(df):
    """
    Generate embeddings for all health articles and store them in ChromaDB.
    This step runs after the analytics pipeline.
    """
    from embeddings.chroma_store import get_chroma_client, get_collection, add_articles_to_collection
    logging.info("Starting embeddings pipeline")

    try:
        # Set up ChromaDB
        client = get_chroma_client()
        collection = get_collection(client)

        # Add articles (skips any already in the collection)
        total = add_articles_to_collection(df, collection, batch_size=100)
        logging.info(f"Embeddings pipeline complete. {total} articles in ChromaDB.")

    except Exception as e:
        logging.error(f"Embeddings pipeline failed: {e}")
        raise

def run_pipeline():
    # from storage.mongo import save_to_mongo, build_scraped_record, build_ocr_record
    # from scraping.scraper import scrape_multiple_pages
    # from ocr.ocr_utils import compare_ocr, ocr_scanned_pdf
    # from parsing.parsers import (
    #     extract_text_from_pdf, extract_text_from_two_column_pdf,
    #     extract_text_from_word, extract_data_from_excel, extract_summary_from_excel
    # )

    # pdf_standard = "../../data/raw/research/health_digest_normal.pdf"
    # pdf_two_column = "../../data/raw/research/health_digest_two_column.pdf"
    # text_standard = extract_text_from_pdf(pdf_standard)
    # save_to_mongo({"text": text_standard}, "PDF Source", {"file_name": "health_digest_normal.pdf", "type": "pdf"})
    # text_two_column = extract_text_from_two_column_pdf(pdf_two_column)
    # save_to_mongo({"text": text_two_column}, "PDF Source", {"file_name": "health_digest_two_column.pdf", "type": "pdf"})
    # logging.info("PDF data processed")

    # word_standard = "../../data/raw/docx/health_digest_normal.docx"
    # word_two_column = "../../data/raw/docx/health_digest_two_column.docx"
    # text_word = extract_text_from_word(word_standard)
    # save_to_mongo({"text": text_word}, "Word Source", {"file_name": "health_digest_normal.docx", "type": "word"})
    # text_word_2 = extract_text_from_word(word_two_column)
    # save_to_mongo({"text": text_word_2}, "Word Source", {"file_name": "health_digest_two_column.docx", "type": "word"})
    # logging.info("Word data processed")

    # excel_path = "../../data/raw/xlsx/health_articles.xlsx"
    # articles_excel = extract_data_from_excel(excel_path)
    # for article in articles_excel:
    #     save_to_mongo(article, "Excel Source", {"file_name": "health_articles.xlsx", "type": "excel"})
    # summary = extract_summary_from_excel(excel_path)
    # save_to_mongo(summary, "Excel Summary", {"file_name": "health_articles_summary.xlsx", "type": "excel_summary"})
    # logging.info("Excel data processed")

    # try:
    #     logging.info("Starting OCR...")
    #     raw_text, processed_text = compare_ocr("../../data/raw/images/PMC3931379_830fig1.png")
    #     save_to_mongo({"raw_text": raw_text, "processed_text": processed_text}, "OCR Image Source", {"file_name": "test.png", "type": "image_ocr"})
    #     logging.info("OCR from image finished.")
    # except Exception as e:
    #     logging.error(f"OCR image error: {e}")

    # try:
    #     logging.info("Starting OCR of scanned PDF...")
    #     pdf_texts = ocr_scanned_pdf("../../data/raw/scanned/DIABETES.pdf")
    #     for page_key, text in pdf_texts.items():
    #         record = build_ocr_record(text, "DIABETES.pdf", page_number=page_key)
    #         save_to_mongo(record["data"], record["source"], {"type": record["type"], "page_number": record["page_number"], "extracted_at": record["extracted_at"]})
    #     logging.info(f"OCR finished. Processed {len(pdf_texts)} pages.")
    # except Exception as e:
    #     logging.error(f"OCR error: {e}")

    # try:
    #     logging.info("Starting multi-page scraping...")
    #     teams = scrape_multiple_pages("https://www.diabetes.org.uk/about-us/news-and-views/search?category=all", max_pages=3)
    #     for team in teams:
    #         record = build_scraped_record(team, "diabetes.org.uk/about-us/news-and-views/search?category=all")
    #         save_to_mongo(record["data"], record["source"], {"type": record["type"], "extracted_at": record["extracted_at"]})
    #     logging.info(f"Multi-page scraping finished. Scraped {len(teams)} teams.")
    # except Exception as e:
    #     logging.error(f"Multi-page scraping error: {e}")

    # run_audio_video_stage()
    # run_analytics()

    # run_cleaning()

    BASE_DIR = Path(__file__).resolve().parents[2]
    cleaned_path = BASE_DIR / "data" / "processed" / "cleaned" / "articles_clean.csv"
    # run_pipeline()
    # run_analytics_pipeline(cleaned_path, mysql_password="root")

    # logging.info("Step 3: Embeddings pipeline")
    # df = pd.read_csv(cleaned_path)
    # run_embeddings_pipeline(df)

    logging.info("Visualizations pipeline")

    run_visualizations_pipeline(cleaned_path)

    logging.info("Pipeline finished successfully")


if __name__ == "__main__":
    run_pipeline()
