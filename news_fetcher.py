import requests
from typing import Dict, List, Any
from config import settings


class NewsFetcherError(Exception):
    pass


class NewsFetcher:
    def __init__(self, api_key: str | None = None):
        # IMPORTANT:
        # api_key=None -> fallback to settings
        # api_key=""   -> explicitly no key (used in tests)
        self.api_key = settings.NEWSAPI_KEY if api_key is None else api_key


    def fetch(self, query: str | None = None, page_size: int | None = None) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise NewsFetcherError("Missing NEWSAPI_KEY in environment (.env).")

        q = query or settings.QUERY
        size = page_size or settings.PAGE_SIZE

        params = {
            "q": q,
            "pageSize": size,
            "language": "en",
            "sortBy": "publishedAt",
        }

        headers = {"X-Api-Key": self.api_key}

        try:
            resp = requests.get(settings.NEWSAPI_ENDPOINT, params=params, headers=headers, timeout=20)
        except requests.RequestException as e:
            raise NewsFetcherError(f"Network error while fetching news: {e}") from e

        if resp.status_code != 200:
            raise NewsFetcherError(f"NewsAPI error {resp.status_code}: {resp.text}")

        data = resp.json()
        articles = data.get("articles", [])

        # Normalize: keep only key fields
        normalized = []
        for a in articles:
            normalized.append(
                {
                    "title": a.get("title"),
                    "source": (a.get("source") or {}).get("name"),
                    "url": a.get("url"),
                    "publishedAt": a.get("publishedAt"),
                    "description": a.get("description"),
                    "content": a.get("content"),
                }
            )
        return normalized
