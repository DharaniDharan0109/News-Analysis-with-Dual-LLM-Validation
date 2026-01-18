import pytest
from llm_validator import OpenRouterValidator, LLMValidatorError


def test_validator_requires_key():
    v = OpenRouterValidator(api_key="")
    with pytest.raises(LLMValidatorError):
        v.validate(
            {"title": "Test", "description": "Test", "content": "Test"},
            {"gist": "x", "sentiment": "neutral", "tone": "informative"},
        )
