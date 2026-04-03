import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraping.scraper import scrape_multiple_pages

from ocr.ocr_utils import compare_ocr, ocr_scanned_pdf
from utils.logger import logging  
from storage.mongo import save_to_mongo, build_scraped_record, build_ocr_record  

from parsing.parsers import (
    extract_text_from_pdf,
    extract_text_from_two_column_pdf,
    extract_text_from_word,
    extract_data_from_excel,
    extract_summary_from_excel
)

def run_pipeline():

    pdf_standard = "../../data/raw/research/health_digest_normal.pdf"
    pdf_two_column = "../../data/raw/research/health_digest_two_column.pdf"

    text_standard = extract_text_from_pdf(pdf_standard)

    save_to_mongo(
        {"text": text_standard},
        "PDF Source",
        {"file_name": "health_digest_normal.pdf", "type": "pdf"}
    )

    text_two_column = extract_text_from_two_column_pdf(pdf_two_column)
    save_to_mongo(
        {"text": text_two_column},
        "PDF Source",
        {"file_name": "health_digest_two_column.pdf", "type": "pdf"}
    )

    logging.info("PDF data processed")

    word_standard = "../../data/raw/docx/health_digest_normal.docx"
    word_two_column = "../../data/raw/docx/health_digest_two_column.docx"

    text_word = extract_text_from_word(word_standard)
    save_to_mongo(
        {"text": text_word},
        "Word Source",
        {"file_name": "health_digest_normal.docx", "type": "word"}
    )

    text_word_2 = extract_text_from_word(word_two_column)
    save_to_mongo(
        {"text": text_word_2},
        "Word Source",
        {"file_name": "health_digest_two_column.docx", "type": "word"}
    )

    logging.info("Word data processed")

    excel_path = "../../data/raw/xlsx/health_articles.xlsx"
    articles_excel = extract_data_from_excel(excel_path)

    for article in articles_excel:
        save_to_mongo(
            article,
            "Excel Source",
            {"file_name": "health_articles.xlsx", "type": "excel"}
        )

    summary = extract_summary_from_excel(excel_path)
    save_to_mongo(
        summary,
        "Excel Summary",
        {"file_name": "health_articles_summary.xlsx", "type": "excel_summary"}
    )

    logging.info("Excel data processed")

    try:
        logging.info("Starting OCR...")
        raw_text, processed_text = compare_ocr("../../data/raw/images/PMC3931379_830fig1.png")

        save_to_mongo(
            {
                "raw_text": raw_text,
                "processed_text": processed_text
            },
            "OCR Image Source",
            {
                "file_name": "test.png",
                "type": "image_ocr"
            }
        )

        logging.info("OCR from image finished.")
    except Exception as e:
        logging.error(f"OCR image error: {e}")

    try:
        logging.info("Starting OCR of scanned PDF...")

        pdf_texts = ocr_scanned_pdf("../../data/raw/scanned/DIABETES.pdf")
        for page_key, text in pdf_texts.items():
            record = build_ocr_record(text, "DIABETES.pdf", page_number=page_key)
            save_to_mongo(
                record["data"],
                record["source"],
                {
                    "type": record["type"],
                    "page_number": record["page_number"],
                    "extracted_at": record["extracted_at"]
                }
            )
        logging.info(f"OCR finished. Processed {len(pdf_texts)} pages.")
    except Exception as e:
        logging.error(f"OCR error: {e}")
    try:
        logging.info("Starting multi-page scraping of teams...")
        teams = scrape_multiple_pages("https://www.diabetes.org.uk/about-us/news-and-views/search?category=all", max_pages=3)

        for team in teams:
            record = build_scraped_record(team, "diabetes.org.uk/about-us/news-and-views/search?category=all")
            save_to_mongo(
                record["data"],
                record["source"],
                {
                    "type": record["type"],
                    "extracted_at": record["extracted_at"]
                }
            )

        logging.info(f"Multi-page scraping finished. Scraped {len(teams)} teams.")
    except Exception as e:
        logging.error(f"Multi-page scraping error: {e}")

    logging.info("Pipeline finished successfully")

if __name__ == "__main__":
    run_pipeline()