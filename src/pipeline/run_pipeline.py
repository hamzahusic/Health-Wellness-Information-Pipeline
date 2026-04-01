import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from utils.logger import logging  
from storage.mongo import save_to_mongo 

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

    logging.info("Pipeline finished successfully")

if __name__ == "__main__":
    run_pipeline()