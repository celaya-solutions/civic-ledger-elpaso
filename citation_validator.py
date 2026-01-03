from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF


class CitationValidator:
    """Lightweight PDF validator that checks for an exact claimed string."""

    def __init__(self, docs_path: Path) -> None:
        self.docs_path = docs_path

    async def validate(self, *, document: str, page: int | None, section: str | None, claimed_text: str) -> str:
        pdf_path = self.docs_path / document
        if not pdf_path.exists():
            return json.dumps({"status": "error", "detail": f"{pdf_path} not found"})

        if not claimed_text or not claimed_text.strip():
            return json.dumps({"status": "error", "detail": "claimed_text is empty"})

        text = ""
        doc = fitz.open(pdf_path)
        try:
            if page:
                idx = max(1, int(page)) - 1
                if idx < 0 or idx >= len(doc):
                    return json.dumps({"status": "error", "detail": f"page {page} out of range"})
                text = doc[idx].get_text() or ""
            else:
                # Full scan
                text = "\n".join([doc[p].get_text() or "" for p in range(len(doc))])
        finally:
            doc.close()

        matches = []
        hay = text or ""
        needle = claimed_text.strip()
        start = 0
        while True:
            pos = hay.find(needle, start)
            if pos == -1:
                break
            a = max(0, pos - 180)
            b = min(len(hay), pos + len(needle) + 180)
            matches.append(hay[a:b].replace("\n", " ").strip())
            start = pos + len(needle)
            if len(matches) >= 5:
                break

        status = "valid" if matches else "not_found"
        return json.dumps({
            "status": status,
            "document": document,
            "page": page,
            "section": section,
            "matches": len(matches),
            "contexts": matches,
        }, indent=2)
