import json
from typing import Dict, Any
import requests

from config import settings


class LLMValidatorError(Exception):
    pass


class OpenRouterValidator:
    """
    LLM#2 - OpenRouter (Mistral)
    Validates Gemini's analysis against the article.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = settings.OPENROUTER_API_KEY if api_key is None else api_key
        self.model = model or settings.OPENROUTER_MODEL

    def validate(self, article: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            raise LLMValidatorError("Missing OPENROUTER_API_KEY in environment (.env).")

        prompt = f"""
You are a strict fact-checker.

Given:
1) A news article
2) An analysis (gist, sentiment, tone)

Your job:
- verify whether the analysis matches the article
- point out any errors or hallucinations
- if incorrect, suggest corrected sentiment/tone and a better gist

Return STRICT JSON ONLY in this schema:
{{
  "valid": true|false,
  "issues": ["..."],
  "corrected": {{
    "gist": "...",
    "sentiment": "positive|negative|neutral",
    "tone": "urgent|analytical|satirical|balanced|critical|optimistic|pessimistic|informative"
  }}
}}

Article:
Title: {article.get("title")}
Description: {article.get("description")}
Content: {article.get("content")}

Analysis:
{json.dumps(analysis, ensure_ascii=False)}
""".strip()

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You only output valid JSON. No markdown."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
        except requests.RequestException as e:
            raise LLMValidatorError(f"Network error calling OpenRouter: {e}") from e

        if resp.status_code != 200:
            raise LLMValidatorError(f"OpenRouter error {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise LLMValidatorError(f"Unexpected OpenRouter response format: {data}") from e

        cleaned = text.strip()
        cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise LLMValidatorError(f"Validator returned non-JSON output: {text}") from e

        return result
