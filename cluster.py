"""Group keywords into topics without a model or an embedding API.

The rule: two keywords belong together when they share their rarest meaningful
token. It is crude, it is instant, and on autocomplete output it lands close
enough to be useful for page planning.

    python3 cluster.py keywords.csv --min-size 3 --out clusters.csv
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict

from kw import tokens


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--min-size", type=int, default=3)
    ap.add_argument("--out", default="clusters.csv")
    args = ap.parse_args()

    with open(args.file, newline="", encoding="utf-8") as fh:
        keywords = [r["keyword"] for r in csv.DictReader(fh) if r.get("keyword")]

    frequency = Counter(t for k in keywords for t in set(tokens(k)))

    clusters: dict[str, list[str]] = defaultdict(list)
    for keyword in keywords:
        ts = [t for t in tokens(keyword) if frequency[t] >= 2]
        if not ts:
            clusters["(unclustered)"].append(keyword)
            continue
        # The rarest shared token is the most specific thing these keywords have in common.
        head = min(ts, key=lambda t: (frequency[t], t))
        clusters[head].append(keyword)

    ranked = sorted(clusters.items(), key=lambda kv: -len(kv[1]))

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["cluster", "size", "keyword"])
        for head, members in ranked:
            for keyword in sorted(members):
                w.writerow([head, len(members), keyword])

    print(f"{len(keywords)} keywords → {len(ranked)} clusters → {args.out}\n")
    for head, members in ranked:
        if len(members) < args.min_size:
            continue
        print(f"{head}  ({len(members)})")
        for keyword in sorted(members)[:6]:
            print(f"    {keyword}")
        if len(members) > 6:
            print(f"    … {len(members) - 6} more")
        print()


if __name__ == "__main__":
    main()
