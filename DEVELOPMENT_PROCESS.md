# DEVELOPMENT_PROCESS.md

## Problem Statement

Build a production-style news analysis pipeline that:

1. fetches political/government related news articles from NewsAPI
2. analyzes each article using an LLM to generate:

   * gist (1–2 sentences)
   * sentiment (positive/negative/neutral)
   * tone (urgent/analytical/satirical/balanced/critical/optimistic/pessimistic/informative)
3. validates the analysis using a second LLM (dual validation) to reduce hallucinations
4. saves results as JSON + a human-readable Markdown report.

This matches Celltron’s expectation of “Engineer + AI as a disciplined team”: break down the problem, implement robust code, handle errors, include tests, and document decisions. 

---

## Breakdown of Tasks (Disciplined Engineering Approach)

Following Celltron’s recommended workflow, I split the assignment into small tasks:

1. **Fetch news** from NewsAPI with filters for India politics/government

   * Output: list of article dicts (JSON)

2. **Normalize + structure** articles into consistent schema

   * Output: cleaned articles with `{title, source, url, publishedAt, description, content}`

3. **LLM#1 Analysis (Sentiment + Tone + Gist)**

   * Output: `{gist, sentiment, tone}`

4. **LLM#2 Validation**

   * Verify LLM#1 output aligns with article content
   * Output: `{valid, issues[], corrected{gist,sentiment,tone}}`

5. **Generate report**

   * Output: `final_results.json` + `final_report.md`

6. **Add tests**

   * Minimum 3 unit tests (keys missing, module logic correctness)

---

## Tools / Stack Used

* **Python 3.12**
* `requests` for HTTP calls
* `python-dotenv` for environment configuration
* `pytest` for tests
* **NewsAPI** for fetching articles
* **OpenRouter LLM** for sentiment analysis and validation

---

## Key Design Decisions

### Decision 1: Use OpenRouter `google/gemma-2-9b-it` as LLM#1 (Sentiment, Tone, Gist)

Initially I implemented Gemini as LLM#1, but during execution I faced:

1. **404 model errors** (model not found / unsupported for generateContent)
2. **429 quota exhausted** (free tier quota reported as 0 / rate limits)

This caused articles to fallback into neutral sentiment outputs due to controlled error handling.

✅ To ensure the pipeline produces meaningful analysis consistently, I moved LLM#1 sentiment analysis to OpenRouter using:

**LLM#1 (Analyzer Model):** `google/gemma-2-9b-it`

This decision improves reliability and aligns with Celltron’s engineering mindset:

* do not get blocked by unstable API quota/model issues
* ship a working system with correct outputs
* document the trade-off transparently

---

### Decision 2: Dual LLM Validation Still Preserved

Even after switching LLM#1 to OpenRouter, I preserved “dual LLM validation” by using two distinct models:

* **LLM#1 (Analyzer):** OpenRouter `google/gemma-2-9b-it`

  * fast summarization + sentiment classification
* **LLM#2 (Validator):** OpenRouter `mistralai/mistral-7b-instruct`

  * strict checking + correction suggestions

This maintains the assignment requirement of using a second LLM for validation and reduces single-model bias.

---

## Prompt Strategy

### LLM#1 Analyzer Prompt

Goal: extract structured analysis as JSON only.

**Prompt used:**

* Provide title + description + content
* enforce strict JSON schema
* prevent markdown output

Expected JSON schema:

```json
{
  "gist": "1-2 sentence summary",
  "sentiment": "positive|negative|neutral",
  "tone": "urgent|analytical|satirical|balanced|critical|optimistic|pessimistic|informative"
}
```

---

### LLM#2 Validator Prompt

Goal: verify the analysis matches the article and remove hallucinations.

Validator JSON schema:

```json
{
  "valid": true|false,
  "issues": ["..."],
  "corrected": {
    "gist": "...",
    "sentiment": "positive|negative|neutral",
    "tone": "urgent|analytical|satirical|balanced|critical|optimistic|pessimistic|informative"
  }
}
```

If LLM#2 finds mismatch/hallucinations, the corrected output becomes the final result.

---

## Iterations and Improvements

### Issue 1: pytest import errors on Windows

While running pytest, tests could not import root modules (ModuleNotFoundError).
Fix: added `tests/conftest.py` to append project root to `sys.path`.

---

### Issue 2: API key fallback causing failing tests

The initial constructor logic used:

```python
self.api_key = api_key or settings.KEY
```

This incorrectly fell back to `.env` settings even when `api_key=""` was passed intentionally in tests.

Fix:

* `None` means “fallback”
* empty string means “explicitly missing”

This improved test reliability and correctness.

---

### Issue 3: Gemini model instability (404) and quota issues (429)

Gemini integration failed due to:

* model availability constraints (404)
* quota/rate limits (429)

Fix:

* switched primary analyzer to OpenRouter model `google/gemma-2-9b-it`
* retained validator as a separate OpenRouter model (`mistralai/mistral-7b-instruct`)

This ensured the pipeline produces meaningful results consistently.

---

## Error Handling (Production mindset)

* NewsAPI network failures and invalid responses → raised as clear exceptions
* LLM API failures (timeout/invalid JSON/rate limits) → handled gracefully and logged as issues
* Pipeline continues execution even if some articles fail analysis
* Validator step ensures traceability of errors and corrected output.

---

## Testing Strategy

Included at least 3 unit tests:

1. Fetcher should fail when no NewsAPI key
2. Analyzer should fail when no OpenRouter API key
3. Validator should fail when no OpenRouter API key

Tests ensure module-level correctness and prevent silent failure.

---

## What I Learned / What I'd Improve Next

* LLM APIs can change rapidly (model names, quotas, supported endpoints).

* Robust pipelines need:

  * throttling
  * retries
  * fallbacks between providers

* In future iterations:

  * add response caching
  * add integration tests for full pipeline with mocked HTTP
  * improve sentiment scoring with confidence levels.

---

## Final Deliverables Produced

* `output/raw_articles.json`
* `output/analysis_results.json`
* `output/final_results.json`
* `output/final_report.md`
* Unit tests in `tests/`
* This documentation file describing disciplined task-by-task development
