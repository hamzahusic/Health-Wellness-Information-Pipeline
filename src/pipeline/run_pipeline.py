import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analytics.quality_report import full_quality_report, outlier_report, save_missing_heatmap

from analytics.data_loader import chunked_stats, load_from_mongodb, memory_comparison, save_to_csv, optimise_dtypes
from analytics.numpy_ops import demonstrate_array_creation, vectorized_operations
from scraping.scraper import scrape_multiple_pages

from ocr.ocr_utils import compare_ocr, ocr_scanned_pdf
from utils.logger import logging  
from storage.mongo import save_to_mongo, build_scraped_record, build_ocr_record, get_db, save_transcript

from parsing.parsers import (
    extract_text_from_pdf,
    extract_text_from_two_column_pdf,
    extract_text_from_word,
    extract_data_from_excel,
    extract_summary_from_excel
)

from audio_processing.loader      import inspect_audio, load_audio
from audio_processing.processor   import trim_audio, apply_fades, export_audio
from audio_processing.transcriber import (
    transcribe_audio, save_transcript_json,
    save_transcript_txt, save_transcript_srt
)
from video_processing.loader       import inspect_video, extract_audio_from_video
from video_processing.frame_extractor import extract_keyframes

from pathlib import Path

import logging
import numpy as np
from analytics.explorer import (
    extract_publish_year, inspect_shape, plot_distributions,
    value_counts_report, print_info, describe_numeric
)
from analytics.selector import boolean_filter, isin_filter, loc_filter
from analytics.regex_ops import health_keyword_count, top_health_keywords, normalize_author

logger = logging.getLogger(__name__)

from cleaning.clean_pipeline import run_cleaning_pipeline

def run_cleaning():

    logging.info('=== Lab 9: Data Cleaning ===')

    raw_csv = Path('data/processed/analytics/articles.csv')
    if not raw_csv.exists():
        logging.warning('articles.csv not found at %s', raw_csv)
        return None

    df_raw = pd.read_csv(raw_csv, low_memory=False)
    logging.info('Loaded %d rows from %s', len(df_raw), raw_csv)

    df_clean = run_cleaning_pipeline(df_raw, save=True)
    logging.info('Cleaning complete: %d rows saved to data/processed/cleaned/', len(df_clean))
    return df_clean
    
def run_analytics():

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
        import pandas as pd
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
    logging.info('=== Audio/Video Processing Stage ===')
    db = get_db()

    # AUDIO
    for audio_file in Path('data/raw/audio').glob('*.mp3'):
        try:
            logging.info(f'Processing audio: {audio_file.name}')

            audio = load_audio(str(audio_file))
            trimmed = trim_audio(audio, 0, min(30000, len(audio)))
            faded = apply_fades(trimmed)

            export_audio(
                faded,
                f'data/processed/audio/{audio_file.stem}_clip.mp3'
            )

            result = transcribe_audio(str(audio_file))

            j = f'data/processed/transcripts/{audio_file.stem}.json'
            t = f'data/processed/transcripts/{audio_file.stem}.txt'
            s = f'data/processed/transcripts/{audio_file.stem}.srt'

            save_transcript_json(result, j)
            save_transcript_txt(result, t)
            save_transcript_srt(result, s)

            save_transcript(db, result, str(audio_file), 'audio',
                            json_path=j, txt_path=t, srt_path=s)

        except Exception as e:
            logging.error(f'Audio error: {e}')

    # VIDEO
    for video_file in Path('../../data/raw/video').glob('*.mp4'):
        try:
            logging.info(f'Processing video: {video_file.name}')

            extract_keyframes(
                str(video_file),
                f'../../data/processed/frames/{video_file.stem}/'
            )

            audio_out = f'../../data/processed/audio/{video_file.stem}.mp3'
            extract_audio_from_video(str(video_file), audio_out)

            result = transcribe_audio(audio_out)

            j = f'../../data/processed/transcripts/{video_file.stem}.json'
            t = f'../../data/processed/transcripts/{video_file.stem}.txt'
            s = f'../../data/processed/transcripts/{video_file.stem}.srt'

            save_transcript_json(result, j)
            save_transcript_txt(result, t)
            save_transcript_srt(result, s)

            save_transcript(db, result, str(video_file), 'video',
                            json_path=j, txt_path=t, srt_path=s)

        except Exception as e:
            logging.error(f'Video error: {e}')

    logging.info('=== Audio/Video Processing Stage Complete ===')

def run_pipeline():

    # pdf_standard = "../../data/raw/research/health_digest_normal.pdf"
    # pdf_two_column = "../../data/raw/research/health_digest_two_column.pdf"

    # text_standard = extract_text_from_pdf(pdf_standard)

    # save_to_mongo(
    #     {"text": text_standard},
    #     "PDF Source",
    #     {"file_name": "health_digest_normal.pdf", "type": "pdf"}
    # )

    # text_two_column = extract_text_from_two_column_pdf(pdf_two_column)
    # save_to_mongo(
    #     {"text": text_two_column},
    #     "PDF Source",
    #     {"file_name": "health_digest_two_column.pdf", "type": "pdf"}
    # )

    # logging.info("PDF data processed")

    # word_standard = "../../data/raw/docx/health_digest_normal.docx"
    # word_two_column = "../../data/raw/docx/health_digest_two_column.docx"

    # text_word = extract_text_from_word(word_standard)
    # save_to_mongo(
    #     {"text": text_word},
    #     "Word Source",
    #     {"file_name": "health_digest_normal.docx", "type": "word"}
    # )

    # text_word_2 = extract_text_from_word(word_two_column)
    # save_to_mongo(
    #     {"text": text_word_2},
    #     "Word Source",
    #     {"file_name": "health_digest_two_column.docx", "type": "word"}
    # )

    # logging.info("Word data processed")

    # excel_path = "../../data/raw/xlsx/health_articles.xlsx"
    # articles_excel = extract_data_from_excel(excel_path)

    # for article in articles_excel:
    #     save_to_mongo(
    #         article,
    #         "Excel Source",
    #         {"file_name": "health_articles.xlsx", "type": "excel"}
    #     )

    # summary = extract_summary_from_excel(excel_path)
    # save_to_mongo(
    #     summary,
    #     "Excel Summary",
    #     {"file_name": "health_articles_summary.xlsx", "type": "excel_summary"}
    # )

    # logging.info("Excel data processed")

    # try:
    #     logging.info("Starting OCR...")
    #     raw_text, processed_text = compare_ocr("../../data/raw/images/PMC3931379_830fig1.png")

    #     save_to_mongo(
    #         {
    #             "raw_text": raw_text,
    #             "processed_text": processed_text
    #         },
    #         "OCR Image Source",
    #         {
    #             "file_name": "test.png",
    #             "type": "image_ocr"
    #         }
    #     )

    #     logging.info("OCR from image finished.")
    # except Exception as e:
    #     logging.error(f"OCR image error: {e}")

    # try:
    #     logging.info("Starting OCR of scanned PDF...")

    #     pdf_texts = ocr_scanned_pdf("../../data/raw/scanned/DIABETES.pdf")
    #     for page_key, text in pdf_texts.items():
    #         record = build_ocr_record(text, "DIABETES.pdf", page_number=page_key)
    #         save_to_mongo(
    #             record["data"],
    #             record["source"],
    #             {
    #                 "type": record["type"],
    #                 "page_number": record["page_number"],
    #                 "extracted_at": record["extracted_at"]
    #             }
    #         )
    #     logging.info(f"OCR finished. Processed {len(pdf_texts)} pages.")
    # except Exception as e:
    #     logging.error(f"OCR error: {e}")
    # try:
    #     logging.info("Starting multi-page scraping of teams...")
    #     teams = scrape_multiple_pages("https://www.diabetes.org.uk/about-us/news-and-views/search?category=all", max_pages=3)

    #     for team in teams:
    #         record = build_scraped_record(team, "diabetes.org.uk/about-us/news-and-views/search?category=all")
    #         save_to_mongo(
    #             record["data"],
    #             record["source"],
    #             {
    #                 "type": record["type"],
    #                 "extracted_at": record["extracted_at"]
    #             }
    #         )

    #     logging.info(f"Multi-page scraping finished. Scraped {len(teams)} teams.")
    # except Exception as e:
    #     logging.error(f"Multi-page scraping error: {e}")
    
    # run_audio_video_stage()
    # run_analytics()
    
    run_cleaning()
    logging.info("Pipeline finished successfully")

if __name__ == "__main__":
    run_pipeline()