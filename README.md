# News Analyzer

A production-style news analysis pipeline that fetches Indian politics/government news articles from NewsAPI, generates structured analysis using an LLM, validates the analysis using a second LLM, and produces JSON + Markdown outputs.


---

## Features

* Fetches latest news using **NewsAPI**
* LLM-based structured analysis:

  * **gist** (1–2 sentence summary)
  * **sentiment** (`positive|negative|neutral`)
  * **tone** (`urgent|analytical|satirical|balanced|critical|optimistic|pessimistic|informative`)
* Dual-model validation workflow:

  * **LLM#1** → generates analysis
  * **LLM#2** → validates and corrects hallucinations
* Saves results to:

  * JSON files (`raw_articles.json`, `analysis_results.json`, `final_results.json`)
  * Markdown report (`final_report.md`)
* Unit tests included (`pytest`)

---

## Folder Structure

```text
news-analyzer/
├── main.py
├── config.py
├── utils.py
├── news_fetcher.py
├── llm_analyzer.py
├── llm_validator.py
├── report_builder.py
├── DEVELOPMENT_PROCESS.md
├── requirements.txt
├── .env.example
├── output/
│   ├── raw_articles.json
│   ├── analysis_results.json
│   ├── final_results.json
│   └── final_report.md
└── tests/
    ├── conftest.py
    ├── test_fetcher.py
    ├── test_analyzer.py
    └── test_validator.py
```

---

## Setup

### 1) Create virtual environment

```bash
python -m venv .venv
```

Activate:

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\activate
```

**Mac/Linux**

```bash
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create `.env` file using `.env.example`.

```env
NEWSAPI_KEY=your_newsapi_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional
QUERY=India politics OR India government
PAGE_SIZE=12

# Optional model overrides
OPENROUTER_ANALYZER_MODEL=google/gemma-2-9b-it
OPENROUTER_VALIDATOR_MODEL=mistralai/mistral-7b-instruct
```

---

## Run the Pipeline

```bash
python main.py
```

Outputs will be written to:

```text
output/
  raw_articles.json
  analysis_results.json
  final_results.json
  final_report.md
```

---

## Run Tests

```bash
pytest -q
```

---

## LLM Design (Dual Validation)

This project uses a two-stage LLM approach:

### LLM#1 — Analyzer

Generates structured JSON:

```json
{
  "gist": "...",
  "sentiment": "neutral",
  "tone": "analytical"
}
```

### LLM#2 — Validator

Validates the above output against the article text and returns:

```json
{
  "valid": true,
  "issues": [],
  "corrected": {
    "gist": "...",
    "sentiment": "neutral",
    "tone": "analytical"
  }
}
```

If LLM#2 marks output invalid, the corrected output becomes the final result.

---

## Notes / Reliability

To ensure consistent execution and usable results, OpenRouter is used for sentiment analysis and validation.

The system is designed with:

* clear error handling
* graceful fallbacks
* traceable outputs

---

## Documentation

* `DEVELOPMENT_PROCESS.md` explains:

  * breakdown into tasks
  * prompt strategy
  * iterations and fixes
  * design decisions and trade-offs

---
