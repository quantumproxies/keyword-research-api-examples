"""Expand a seed into keywords, split by the probe family that found each one.

    python3 expand.py "residential proxy" --country us --max 300 --out keywords.csv
    python3 expand.py "web scraping" --modes seed questions comparisons
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter

from kw import collect, is_question

ALL_MODES = ["seed", "alphabet", "questions", "prepositions", "comparisons"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed")
    ap.add_argument("--modes", nargs="*", default=["seed", "questions", "alphabet"],
                    choices=ALL_MODES)
    ap.add_argument("--country", default="us")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--max", type=int, default=200)
    ap.add_argument("--out", default="keywords.csv")
    args = ap.parse_args()

    rows = collect("keyword_ideas", seed=args.seed, modes=args.modes,
                   country=args.country, lang=args.lang, max_results=args.max)

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["rank", "keyword", "seed", "probe", "mode",
                                           "relevance", "type"], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    by_mode = Counter(r.get("mode") for r in rows)
    questions = [r for r in rows if is_question(r.get("keyword", ""))]
    long_tail = [r for r in rows if len((r.get("keyword") or "").split()) >= 4]

    print(f"{len(rows)} keywords for {args.seed!r} → {args.out}   "
          f"(about ${len(rows) * 0.0002:.3f})\n")
    for mode, n in by_mode.most_common():
        print(f"  {mode:<14} {n:>4}")
    print(f"\n{len(questions)} questions, {len(long_tail)} four-words-or-longer\n")

    for row in rows[:25]:
        print(f"  {row.get('mode', ''):<13} {row.get('keyword')}")


if __name__ == "__main__":
    main()
