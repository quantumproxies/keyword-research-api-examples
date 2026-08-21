"""Client and text helpers for the keyword examples."""
from __future__ import annotations

import os
import re
import time
from typing import Any

import requests

BASE = "https://api.quanticdata.io/v1"
_s = requests.Session()

QUESTION_WORDS = ("how", "what", "why", "when", "where", "which", "who",
                  "can", "is", "are", "does", "do", "should", "will")
STOP = {"the", "a", "an", "for", "to", "of", "in", "on", "and", "or", "with", "vs", "best"}


def _h() -> dict[str, str]:
    key = os.environ.get("QUANTICDATA_API_KEY")
    if not key:
        raise SystemExit("set QUANTICDATA_API_KEY — https://app.quanticdata.io/register")
    return {"Authorization": f"Bearer {key}"}


def collect(slug: str, **input_: Any) -> list[dict]:
    payload = {k: v for k, v in input_.items() if v not in (None, "", [], False)}
    r = _s.post(f"{BASE}/scraper/collectors/{slug}/run", json=payload, headers=_h(), timeout=300)
    body = r.json()
    if body.get("type") == "error" or not r.ok:
        raise RuntimeError(f"{slug} ({r.status_code}): {body.get('message')}")

    run = body.get("payload", {})
    while run.get("status") in ("queued", "running"):
        time.sleep(3)
        run = _s.get(f"{BASE}/scraper/collectors/runs/{run['run_id']}",
                     headers=_h(), timeout=60).json().get("payload", {})
    return run.get("results") or []


def serp(query: str, **params: Any) -> dict:
    r = _s.post(f"{BASE}/serp", json={"query": query, **params}, headers=_h(), timeout=120)
    body = r.json()
    if body.get("type") == "error" or not r.ok:
        raise RuntimeError(f"serp ({r.status_code}): {body.get('message')}")
    return body.get("payload", {})


def tokens(keyword: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9']+", (keyword or "").lower()) if t not in STOP]


def is_question(keyword: str) -> bool:
    words = (keyword or "").lower().split()
    return bool(words) and (words[0] in QUESTION_WORDS or keyword.strip().endswith("?"))
