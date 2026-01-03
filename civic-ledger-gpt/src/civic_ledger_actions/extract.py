\
from __future__ import annotations

import re
from typing import Iterable

from .models import Fact, Citation


def _make_snippet(text: str, start: int, end: int, window: int = 220) -> str:
    a = max(0, start - window)
    b = min(len(text), end + window)
    snippet = text[a:b].replace("\n", " ").strip()
    return snippet


def extract_facts_from_text(
    *,
    document_id: str,
    text: str,
    url: str | None,
    out_path: str | None,
    title: str | None,
    published_at: str | None,
    fetched_at: str | None,
    search_terms: list[str],
    max_snippets: int,
) -> tuple[list[Fact], list[str]]:
    facts: list[Fact] = []
    red: list[str] = []

    if not text or not text.strip():
        red.append("No extracted text available for this document.")
        return facts, red

    terms = [t.strip() for t in search_terms if t.strip()]
    if not terms:
        red.append("No search_terms provided; cannot extract targeted snippets.")
        return facts, red

    lower = text.lower()
    for term in terms:
        t = term.lower()
        idx = 0
        hits = 0
        while hits < max_snippets:
            pos = lower.find(t, idx)
            if pos == -1:
                break
            start = pos
            end = pos + len(t)
            snippet = _make_snippet(text, start, end)
            citation = Citation(
                document_id=document_id,
                document=title,
                url=url,
                out_path=out_path,
                published_at=published_at,
                fetched_at=fetched_at,
                location=f"offset:{start}-{end}",
            )
            facts.append(Fact(
                color="GREEN",
                claim=f"Snippet match for term: {term}",
                citation=citation,
                notes=snippet,
            ))
            idx = end
            hits += 1

    if not facts:
        red.append("No matches found for provided search_terms.")
    return facts[:max_snippets], red
