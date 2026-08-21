# Keyword research API — autocomplete expansion at $0.0002 a keyword

The [`keyword_ideas` collector](https://quanticdata.io/collectors/keyword-research-api/) takes a
seed and expands it through **real Google autocomplete probes**, returning up to 500 suggestions
per run with the probe that produced each one. No keyword database, no monthly seat — you are
reading what the engine itself suggests, per country and language.

**$0.0002 per keyword.** A 500-keyword expansion costs ten cents.

```bash
pip install requests
export QUANTICDATA_API_KEY=qd_live_your_key_here

python3 expand.py "residential proxy" --country us --max 300 --out keywords.csv
python3 questions.py "web scraping" --country us          # question-shaped queries only
python3 cluster.py keywords.csv --out clusters.csv        # group by shared head term
python3 validate.py keywords.csv --top 40                 # check who ranks, on real SERPs
```

## Files

| File | What it does |
|---|---|
| [`kw.py`](kw.py) | collector client + tokenisation helpers |
| [`expand.py`](expand.py) | seed → keywords, split by expansion mode |
| [`questions.py`](questions.py) | the `questions` mode alone — how/what/why/can queries for FAQ and AEO work |
| [`cluster.py`](cluster.py) | cheap, dependency-free clustering by shared head terms |
| [`validate.py`](validate.py) | run the winners through the SERP API and see who actually ranks |

## Expansion modes

`modes` picks which probe families run. Default is `["seed", "questions", "alphabet"]`.

| Mode | What it probes | Typical use |
|---|---|---|
| `seed` | the seed alone | the core suggestions |
| `alphabet` | `seed a`, `seed b`, … `seed z` | broadest coverage, most volume |
| `questions` | how/what/why/when/where/which/can/is/does/are + seed | FAQ blocks, AI Overview targets |
| `prepositions` | for/with/without/near/vs/like/to/in | intent-qualified long tail |
| `comparisons` | `seed vs`, `seed or`, `seed like`, `seed alternative` | competitor and alternative pages |

## Output row

```jsonc
{ "rank": 1, "keyword": "residential proxy free trial", "seed": "residential proxy",
  "probe": "residential proxy f", "mode": "alphabet",
  "relevance": 0.82, "type": "suggestion" }
```

`probe` is the exact string sent to autocomplete — keep it, because it explains *why* a
suggestion appeared and lets you re-run one branch without re-running everything.

## What this is and is not

It is the **demand shape**: what people actually type, in the market you asked for, today.
That is exactly what you need for page and FAQ planning, and it is fresher than any index.

It is **not search volume**. Autocomplete has no volume attached, and any tool that claims a
number for a five-word long-tail query is modelling, not measuring. If you need volumes, pair
these keywords with your own Search Console data or a volume provider — and use the
`relevance` field only as an ordering hint within a run.

For "does anyone actually rank for this", `validate.py` runs the keywords through the
[SERP API](https://quanticdata.io/serp-api/) and reports result counts, the top domains and
whether the SERP looks commercial.

## Related

- [Keyword research API](https://quanticdata.io/collectors/keyword-research-api/) · [SERP API](https://quanticdata.io/serp-api/) · [Google Search Results API](https://quanticdata.io/collectors/google-search-results-api/)
- [How a SERP API works](https://quanticdata.io/blog/how-a-serp-api-works/) · [How to perform an SEO audit](https://quanticdata.io/blog/how-to-perform-an-seo-audit/)
- [SEO Audit API](https://quanticdata.io/seo-audit/)

MIT licensed.
