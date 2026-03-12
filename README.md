# Health-Wellness-Information-Pipeline

## Project Description
A diabetes-focused data pipeline that collects health information across multiple formats — research papers, medical images, news articles, and podcast audio — normalizes them into a unified schema, and makes them searchable in one place.

## Data Sources

| Type | Source | Endpoint |
|------|--------|----------|
| PDF | PubMed Central | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=diabetes+treatment&retmode=json` |
| Image | Open-i NLM | `https://openi.nlm.nih.gov/api/search?query=diabetes&m=1&n=10` |
| Text | NewsAPI | `https://newsapi.org/v2/everything?q=diabetes&apiKey=YOUR_KEY` |
| Audio | YouTube / Buzzsprout RSS | `https://feeds.buzzsprout.com/1087782.rss` |

## Data Types
PDF, text, audio, image

## Expected Challenges
- OCR accuracy on low-quality or scanned medical PDFs
- Audio transcription errors in medical terminology
- Rate limiting on NewsAPI free tier
- Data deduplication across overlapping sources
- Schema normalization across different data structures

## Pipeline Architecture Diagram
<img width="1994" height="372" alt="image" src="https://github.com/user-attachments/assets/1c958d21-1cf1-4b50-8715-1654842cd519" />

## Success Criteria
- Successfully ingest data from all 4 source types without pipeline failure
- Audio transcription word error rate ≤ 15%
- End-to-end pipeline runs in under 30 minutes for a daily batch
- Unified schema applied consistently across all data types
- Searchable, queryable output available via a simple API or dashboard
