import os
import pytest
from news_fetcher import NewsFetcher, NewsFetcherError


def test_fetcher_requires_api_key(monkeypatch):
    monkeypatch.setenv("NEWSAPI_KEY", "")
    f = NewsFetcher(api_key="")
    with pytest.raises(NewsFetcherError):
        f.fetch(query="India politics", page_size=1)
