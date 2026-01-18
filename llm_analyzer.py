import json
import requests
from typing import Dict, Any
from config import settings


class LLMAnalyzerError(Exception):
    pass


class OpenRouterAnalyzer:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = settings.OPENROUTER_API_KEY if api_key is None else api_key
        self.model = model or "google/gemma-2-9b-it" 

    def analyze(self, article: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            raise LLMAnalyzerError("Missing OPENROUTER_API_KEY in environment (.env).")

        prompt = f"""
You are a professional news analyst.

Analyze this news article and return STRICT JSON ONLY:
{{
  "gist": "1-2 sentence summary",
  "sentiment": "positive|negative|neutral",
  "tone": "urgent|analytical|satirical|balanced|critical|optimistic|pessimistic|informative"
}}

Article:
Title: {article.get("title")}
Description: {article.get("description")}
Content: {article.get("content")}
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

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            raise LLMAnalyzerError(f"OpenRouter error {resp.status_code}: {resp.text}")

        data = resp.json()
        text = data["choices"][0]["message"]["content"].strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise LLMAnalyzerError(f"Analyzer returned non-JSON output: {text}") from e
