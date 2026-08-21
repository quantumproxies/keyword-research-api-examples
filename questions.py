"""Question-shaped queries only — the raw material for FAQ blocks and AI answers.

Grouped by interrogative, because "how do I …" and "is … legal" are different
kinds of page: one is a tutorial, the other is a definitional answer that
assistants like to quote.

    python3 questions.py "web scraping" --country us --max 300
"""
from __future__ import annotations

import argparse
from collections import defaultdict

from kw import QUESTION_WORDS, collect, is_question


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed")
    ap.add_argument("--country", default="us")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--max", type=int, default=200)
    args = ap.parse_args()

    rows = collect("keyword_ideas", seed=args.seed, modes=["questions", "prepositions"],
                   country=args.country, lang=args.lang, max_results=args.max)

    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        keyword = row.get("keyword") or ""
        if not is_question(keyword):
            continue
        head = keyword.lower().split()[0]
        grouped[head if head in QUESTION_WORDS else "other"].append(keyword)

    total = sum(len(v) for v in grouped.values())
    print(f"{total} question keywords out of {len(rows)} suggestions\n")

    for head in QUESTION_WORDS + ("other",):
        items = grouped.get(head)
        if not items:
            continue
        print(f"{head.upper()} ({len(items)})")
        for keyword in sorted(set(items))[:12]:
            print(f"  - {keyword}")
        print()


if __name__ == "__main__":
    main()
