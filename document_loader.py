"""
Lightweight PDF loader with simple substring search (no vector DB dependency).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class DocumentLoader:
    def __init__(self, docs_path: str) -> None:
        self.docs_path = Path(docs_path)
        if not self.docs_path.exists():
            logger.warning("docs_path does not exist: %s", self.docs_path)

    def _pdf_pages(self, pdf_path: Path) -> list[str]:
        """Return all pages' text from a PDF."""
        pages: list[str] = []
        doc = fitz.open(pdf_path)
        try:
            for page in doc:
                pages.append(page.get_text() or "")
        finally:
            doc.close()
        return pages

    def _iter_pdf_files(self, category_filter: str | None = None) -> Iterable[Path]:
        for pdf in self.docs_path.rglob("*.pdf"):
            if category_filter and category_filter not in str(pdf):
                continue
            yield pdf

    def _match_jurisdiction(self, pdf: Path, jurisdiction: str) -> bool:
        name = pdf.name.lower()
        if jurisdiction == "texas":
            return name.startswith("tx-") or "texas" in name
        if jurisdiction == "new_mexico":
            return name.startswith("nm-") or "newmexico" in name or "new-mexico" in name
        return True

    def _make_snippet(self, text: str, start: int, end: int, window: int = 240) -> str:
        a = max(0, start - window)
        b = min(len(text), end + window)
        return text[a:b].replace("\n", " ").strip()

    async def search_statutes(self, jurisdiction: str, topic: str, query: str) -> str:
        """Naive substring search over PDFs under docs/."""
        if not query or not query.strip():
            return json.dumps({"citations": [], "confidence": "RED", "detail": "query is empty"}, indent=2)

        matches = []
        for pdf in self._iter_pdf_files():
            if not self._match_jurisdiction(pdf, jurisdiction):
                continue
            pages = self._pdf_pages(pdf)
            for idx, page_text in enumerate(pages):
                pos = page_text.lower().find(query.lower())
                if pos == -1:
                    continue
                matches.append({
                    "statute": pdf.stem,
                    "text": self._make_snippet(page_text, pos, pos + len(query)),
                    "page": idx + 1,
                    "source": pdf.name,
                })
                if len(matches) >= 5:
                    break
            if len(matches) >= 5:
                break

        return json.dumps({
            "citations": matches,
            "confidence": "GREEN" if matches else "RED",
            "topic": topic,
        }, indent=2)

    async def load_precedent(self, jurisdiction: str, document_type: str, topic: str) -> str:
        """Return concatenated text for precedent PDFs matching jurisdiction prefix."""
        combined = []
        src = "Unknown"
        for pdf in self._iter_pdf_files():
            if not pdf.name.lower().startswith(jurisdiction):
                continue
            pages = self._pdf_pages(pdf)
            src = pdf.name
            combined.extend(pages)
            if len(combined) > 20:  # cap to avoid huge responses
                break

        full_text = "\n\n".join(combined)
        return json.dumps({
            "document_title": f"{jurisdiction.replace('_', ' ').title()} {document_type.replace('_', ' ').title()}",
            "full_text": full_text[:2000] + "..." if len(full_text) > 2000 else full_text,
            "source": src,
            "topic": topic,
            "adaptability": "requires_modification",
        }, indent=2)

    async def extract_minutes(self, document: str, search_terms: list[str], date_range: str) -> str:
        """Search a specific PDF for search_terms."""
        pdf_path = self.docs_path / document
        if not pdf_path.exists():
            return json.dumps({"document": document, "matches": [], "date_range": date_range, "error": "not found"}, indent=2)

        pages = self._pdf_pages(pdf_path)
        matches = []
        for term in search_terms:
            lt = term.lower()
            for idx, page_text in enumerate(pages):
                pos = page_text.lower().find(lt)
                if pos == -1:
                    continue
                matches.append({
                    "search_term": term,
                    "page": idx + 1,
                    "context": self._make_snippet(page_text, pos, pos + len(term)),
                })
                if len(matches) >= 10:
                    break
            if len(matches) >= 10:
                break

        return json.dumps({
            "document": document,
            "matches": matches,
            "date_range": date_range,
        }, indent=2)

    async def load_resource(self, uri: str) -> str:
        """Load full text of all PDFs (or a single document if uri encodes a name)."""
        name = uri.split("/")[-1]
        if name and name != "docs":
            pdf_path = self.docs_path / name
            if pdf_path.exists():
                return "\n\n".join(self._pdf_pages(pdf_path))

        all_text = []
        for pdf in self._iter_pdf_files():
            all_text.extend(self._pdf_pages(pdf))
        return "\n\n".join(all_text)
