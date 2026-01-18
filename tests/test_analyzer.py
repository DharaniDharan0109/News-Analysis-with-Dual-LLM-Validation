import pytest
from llm_analyzer import OpenRouterAnalyzer, LLMAnalyzerError


def test_analyzer_requires_key():
    a = OpenRouterAnalyzer(api_key="")
    with pytest.raises(LLMAnalyzerError):
        a.analyze({"title": "Test", "description": "Test", "content": "Test"})
