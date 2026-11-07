---
title: Resume Screener
emoji: 📄
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Intelligent Resume Screening & Ranking System

An NLP-based web app and REST API that parses resumes (PDF, DOCX, TXT), scores them against a job description using **TF-IDF + cosine similarity**, and returns a ranked shortlist with matched and missing keywords.

**Stack:** Python, NLP (scikit-learn, NLTK), Flask

## Features
- Text-preprocessing pipeline: tokenization, stop-word removal, lemmatization
- TF-IDF (unigrams + bigrams) with cosine similarity scoring
- Batch upload and scoring of multiple resumes
- Handles PDF, DOCX and plain-text resumes
- Web UI **and** REST API
- Shows which job keywords each resume matches or misses

## Project structure
```
resume-screening-system/
├── app.py                  # Flask app (UI + REST API)
├── screener/
│   ├── parser.py           # PDF / DOCX / TXT text extraction
│   ├── preprocess.py       # tokenize -> stop-words -> lemmatize
│   └── ranker.py           # TF-IDF + cosine similarity ranking
├── templates/index.html    # web UI
├── static/style.css
├── sample_data/            # sample job description + 3 resumes
├── tests/test_ranker.py
└── requirements.txt
```

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

Run the tests: `python -m unittest discover -s tests -v`

## API
`POST /api/rank` (multipart/form-data)

| field | type | description |
|---|---|---|
| `job_description` | text | the job description |
| `resumes` | files | one or more `.pdf`, `.docx`, `.txt` |

```bash
curl -X POST http://127.0.0.1:5000/api/rank \
  -F "job_description=Data Analyst with Python and SQL" \
  -F "resumes=@sample_data/resume_asha_patil.txt" \
  -F "resumes=@sample_data/resume_rohan_mehta.txt"
```

Response:
```json
{"count": 2, "ranking": [{"rank": 1, "name": "Asha Patil", "score": 36.8,
  "matched_keywords": ["python", "sql"], "missing_keywords": ["tableau"]}], "skipped": []}
```

`GET /api/health` returns service status.

## How it works
1. Extract text from each uploaded file.
2. Clean it: lowercase, tokenize, drop stop-words, lemmatize.
3. Build TF-IDF vectors for the job description and every resume.
4. Rank resumes by cosine similarity to the job description (shown as 0-100).

## Ideas to extend
- Skill-section extraction and weighting
- Sentence-embedding similarity (e.g. sentence-transformers) alongside TF-IDF
- Export the ranking to CSV
