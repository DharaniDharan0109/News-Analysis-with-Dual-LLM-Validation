from config import settings
from utils import ensure_dir, save_json
from news_fetcher import NewsFetcher
from llm_analyzer import OpenRouterAnalyzer
from llm_validator import OpenRouterValidator
from report_builder import build_markdown_report


def run():
    ensure_dir(settings.OUTPUT_DIR)

    fetcher = NewsFetcher()
    analyzer = OpenRouterAnalyzer()
    validator = OpenRouterValidator()

    print("Fetching news articles...")
    articles = fetcher.fetch()

    save_json(f"{settings.OUTPUT_DIR}/raw_articles.json", articles)
    print(f"Saved raw articles -> {settings.OUTPUT_DIR}/raw_articles.json")

    analysis_results = []
    print("Analyzing with OpenRouter (LLM#1)...")

    for idx, a in enumerate(articles, start=1):
        try:
            llm1 = analyzer.analyze(a)
        except Exception as e:
            llm1 = {"error": str(e), "gist": "", "sentiment": "neutral", "tone": "informative"}

        analysis_results.append({"article": a, "llm1": llm1})
        print(f"  [{idx}/{len(articles)}] analyzed")

    save_json(f"{settings.OUTPUT_DIR}/analysis_results.json", analysis_results)
    print(f"Saved analysis results -> {settings.OUTPUT_DIR}/analysis_results.json")

    final_results = []
    print("Validating with OpenRouter (LLM#2)...")

    for idx, item in enumerate(analysis_results, start=1):
        article = item["article"]
        llm1 = item["llm1"]

        # If analysis had error, skip validator safely
        if "error" in llm1:
            validation = {
                "valid": False,
                "issues": [f"LLM#1 failed: {llm1['error']}"],
                "corrected": {"gist": article.get("description") or "", "sentiment": "neutral", "tone": "informative"},
            }
        else:
            try:
                validation = validator.validate(article, llm1)
            except Exception as e:
                validation = {
                    "valid": False,
                    "issues": [f"LLM#2 failed: {str(e)}"],
                    "corrected": llm1,
                }

        final = validation["corrected"] if not validation.get("valid", False) else llm1

        final_results.append(
            {
                "article": article,
                "llm1": llm1,
                "llm2_validation": validation,
                "final": final,
            }
        )

        print(f"  [{idx}/{len(analysis_results)}] validated")

    report_md = build_markdown_report(final_results)

    save_json(f"{settings.OUTPUT_DIR}/final_results.json", final_results)
    with open(f"{settings.OUTPUT_DIR}/final_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"Saved final report -> {settings.OUTPUT_DIR}/final_report.md")
    print("DONE ✅")


if __name__ == "__main__":
    run()
