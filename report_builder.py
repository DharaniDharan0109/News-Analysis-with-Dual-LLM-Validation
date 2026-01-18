from typing import List, Dict, Any
from utils import now_iso


def build_markdown_report(final_results: List[Dict[str, Any]]) -> str:
    total = len(final_results)
    pos = sum(1 for x in final_results if x["final"]["sentiment"] == "positive")
    neg = sum(1 for x in final_results if x["final"]["sentiment"] == "negative")
    neu = sum(1 for x in final_results if x["final"]["sentiment"] == "neutral")

    lines = []
    lines.append("# News Analysis Report")
    lines.append(f"**Date:** {now_iso()}")
    lines.append(f"**Articles Analyzed:** {total}")
    lines.append("**Source:** NewsAPI")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Positive: {pos} articles")
    lines.append(f"- Negative: {neg} articles")
    lines.append(f"- Neutral: {neu} articles")
    lines.append("")
    lines.append("## Detailed Analysis")

    for i, item in enumerate(final_results, start=1):
        art = item["article"]
        a1 = item["llm1"]
        v2 = item["llm2_validation"]
        final = item["final"]

        lines.append(f'### Article {i}: "{art.get("title")}"')
        lines.append(f"- **Source:** {art.get('source')}")
        lines.append(f"- **Link:** {art.get('url')}")
        lines.append(f"- **Gist:** {final.get('gist')}")
        lines.append(f"- **LLM#1 Sentiment:** {a1.get('sentiment')}")
        lines.append(f"- **LLM#2 Validation:** {'✓ Valid' if v2.get('valid') else '✗ Issues found'}")

        issues = v2.get("issues") or []
        if issues:
            lines.append("  - Issues:")
            for iss in issues[:5]:
                lines.append(f"    - {iss}")

        lines.append(f"- **Tone:** {final.get('tone')}")
        lines.append("")

    return "\n".join(lines)
