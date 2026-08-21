"""Check keywords against real SERPs before you write anything.

Autocomplete tells you people type it. The SERP tells you whether the page you
were about to write already exists twelve times over, and whether the intent is
commercial or informational.

    python3 validate.py keywords.csv --top 40 --country us --out validated.csv
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from kw import serp

SHOP_HINTS = ("amazon.", "ebay.", "etsy.", "walmart.", "/shop", "/product", "/pricing", "/buy")


def host(url: str | None) -> str:
    try:
        return urlparse(url or "").netloc.lower().removeprefix("www.")
    except ValueError:
        return ""


def probe(keyword: str, country: str) -> dict:
    try:
        payload = serp(keyword, country=country, num=10)
    except RuntimeError as exc:
        return {"keyword": keyword, "error": str(exc)}

    organic = payload.get("organic") or []
    hosts = [host(r.get("link")) for r in organic]
    commercial = sum(1 for r in organic
                     if any(h in (r.get("link") or "").lower() for h in SHOP_HINTS))
    return {
        "keyword": keyword,
        "results_count": payload.get("results_count"),
        "top_domains": ", ".join(dict.fromkeys(h for h in hosts if h))[:120],
        "commercial_hits": commercial,
        "has_shopping": bool(payload.get("shopping")),
        "has_local": bool(payload.get("local_pack") or payload.get("places")),
        "related": ", ".join((payload.get("related_searches") or [])[:5]),
        "error": "",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--country", default="us")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--out", default="validated.csv")
    args = ap.parse_args()

    with open(args.file, newline="", encoding="utf-8") as fh:
        keywords = [r["keyword"] for r in csv.DictReader(fh) if r.get("keyword")][: args.top]

    print(f"checking {len(keywords)} keywords on live SERPs "
          f"(about ${len(keywords) * 0.0005:.3f})\n")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(lambda k: probe(k, args.country), keywords))

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["keyword", "results_count", "commercial_hits",
                                           "has_shopping", "has_local", "top_domains",
                                           "related", "error"])
        w.writeheader()
        w.writerows(rows)

    print(f"{'keyword':<40}{'results':>13}{'commercial':>12}  serp features")
    for row in rows:
        if row.get("error"):
            print(f"{row['keyword'][:39]:<40} !! {row['error'][:40]}")
            continue
        features = " ".join(f for f, on in (("shopping", row["has_shopping"]),
                                            ("local", row["has_local"])) if on)
        count = row.get("results_count")
        print(f"{row['keyword'][:39]:<40}{(f'{count:,}' if count else '—'):>13}"
              f"{row['commercial_hits']:>12}  {features}")

    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
