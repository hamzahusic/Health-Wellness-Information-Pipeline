# Health-Wellness-Information-Pipeline

## Project idea description
Aggregate health articles from APIs, scrape wellness blogs, process medical pamphlets (PDF/OCR), extract clinical trial data from Excel, and transcribe health podcast episodes.

## Data sources
https://www.ncbi.nlm.nih.gov/home/develop/api - PubMed/NCBI API for peer-reviewed medical articles
https://clinicaltrials.gov/api/gui - ClinicalTrials.gov API for trial data
Wellness blogs (e.g., Healthline, WebMD) - web scraping
Medical pamphlets - PDF uploads processed via OCR
Health podcast RSS feeds - audio transcription via OpenAI Whisper
Clinical trial spreadsheets - Excel files

## Data types
PDF, text, audio, image, structured tabular data (Excel/CSV)

## Expected challenges
OCR accuracy on low-quality or scanned medical PDFs
Rate limiting and authentication across multiple APIs
Audio transcription errors in medical terminology
Inconsistent formatting across scraped blog sources
Data deduplication across overlapping sources (e.g., same article from API and blog)
HIPAA/privacy considerations when handling any patient-adjacent content
Schema normalization across wildly different data structures

## Pipeline architecture diagram
<img width="1994" height="372" alt="image" src="https://github.com/user-attachments/assets/1c958d21-1cf1-4b50-8715-1654842cd519" />


## Success criteria
Successfully ingest data from all source types without pipeline failure
Audio transcription word error rate ≤ 15% on health podcast content
End-to-end pipeline runs in under 30 minutes for a daily batch
Unified schema applied consistently across all data types
Searchable, queryable output available via a simple API or dashboard
