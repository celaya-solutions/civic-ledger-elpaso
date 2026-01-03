"""
Lightweight PDF/Markdown loader with substring + fuzzy search (no vector DB).
"""

from __future__ import annotations

import json
import logging
import re
import difflib
from pathlib import Path
from typing import Iterable, Any

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class DocumentLoader:
    def __init__(self, docs_path: str) -> None:
        self.docs_path = Path(docs_path)
        if not self.docs_path.exists():
            logger.warning("docs_path does not exist: %s", self.docs_path)

    def _pdf_pages(self, pdf_path: Path) -> list[str]:
        """Extract text from each page of a PDF."""
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

    def _match_jurisdiction(self, path: Path, jurisdiction: str) -> bool:
        """Filter by jurisdiction based on filename."""
        name = path.name.lower()
        if jurisdiction == "texas":
            return any(x in name for x in ("tx", "texas"))
        if jurisdiction == "new_mexico":
            return any(x in name for x in ("nm", "newmexico", "new-mexico", "new_mexico"))
        return True

    def _make_snippet(self, text: str, start: int, end: int, window: int = 240) -> str:
        a = max(0, start - window)
        b = min(len(text), end + window)
        return text[a:b].replace("\n", " ").strip()

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\btx\b", "texas", text)
        text = re.sub(r"\bnm\b", "new mexico", text)
        text = re.sub(r"\bch\b", "chapter", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _best_fuzzy_ratio(norm_query: str, norm_text: str, max_windows: int = 2500) -> tuple[float, int]:
        """Approximate best fuzzy match ratio by sliding token windows."""
        if not norm_query or not norm_text:
            return 0.0, -1

        q_tokens = norm_query.split()
        t_tokens = norm_text.split()
        if not q_tokens or not t_tokens:
            return 0.0, -1

        w = max(3, len(q_tokens))
        total_windows = max(0, len(t_tokens) - w + 1)
        step = 1
        if total_windows > max_windows:
            step = max(1, total_windows // max_windows)

        best_r = 0.0
        best_tok_i = 0
        for i in range(0, total_windows, step):
            cand = " ".join(t_tokens[i : i + w])
            r = difflib.SequenceMatcher(None, norm_query, cand).ratio()
            if r > best_r:
                best_r = r
                best_tok_i = i
                if best_r >= 0.98:
                    break

        prefix = " ".join(t_tokens[:best_tok_i])
        char_i = 0 if not prefix else len(prefix) + 1
        return best_r, char_i

    async def search_statutes(self, jurisdiction: str, topic: str, query: str) -> str:
        """Search Markdown and PDFs for statutes or code references."""
        if not query or not query.strip():
            return json.dumps({
                "citations": [],
                "confidence": "RED",
                "detail": "query is empty",
                "topic": topic,
                "jurisdiction": jurisdiction
            }, indent=2)

        norm_query = self._normalize(query)
        matches: list[dict[str, Any]] = []

        # ---- Markdown search ----
        for md_file in self.docs_path.rglob("*.md"):
            # do not restrict by jurisdiction filename anymore
            print(f"DEBUG scanning {md_file}")
            try:
                text = md_file.read_text(errors="ignore")
            except Exception as e:
                logger.warning("Failed reading %s: %s", md_file, e)
                continue

            norm_text = self._normalize(text)

            # --- Exact match ---
            if norm_query in norm_text:
                pos = norm_text.find(norm_query)
                snippet = self._make_snippet(text, pos, pos + len(query))
                matches.append({
                    "statute": md_file.stem,
                    "text": snippet,
                    "page": 1,
                    "source": md_file.name,
                    "similarity": 1.0,
                    "type": "markdown",
                    "match_type": "exact"
                })
                break

            # --- Fuzzy and heuristic ---
            ratio, approx_pos = self._best_fuzzy_ratio(norm_query, norm_text)
            if ratio >= 0.3 or any(k in norm_text for k in [
                "texas water code chapter 13",
                "water code chapter 13",
                "chapter 13 utility",
                "utility regulation texas"
            ]):
                snippet = text[max(0, approx_pos - 120): approx_pos + 400].replace("\n", " ").strip()
                matches.append({
                    "statute": md_file.stem,
                    "text": snippet,
                    "page": 1,
                    "source": md_file.name,
                    "similarity": round(ratio, 3),
                    "type": "markdown",
                    "match_type": "fuzzy"
                })
                break

        # ---- If no matches, still check PDFs ----
        if not matches:
            for pdf in self._iter_pdf_files():
                try:
                    pages = self._pdf_pages(pdf)
                except Exception as e:
                    logger.warning("Failed opening %s: %s", pdf, e)
                    continue

                for idx, page_text in enumerate(pages):
                    norm_page = self._normalize(page_text)
                    if norm_query in norm_page:
                        pos = norm_page.find(norm_query)
                        snippet = self._make_snippet(page_text, pos, pos + len(query))
                        matches.append({
                            "statute": pdf.stem,
                            "text": snippet,
                            "page": idx + 1,
                            "source": pdf.name,
                            "similarity": 1.0,
                            "type": "pdf",
                            "match_type": "exact"
                        })
                        break
                if matches:
                    break

        confidence = "GREEN" if matches else "RED"
        return json.dumps({
            "citations": matches,
            "confidence": confidence,
            "topic": topic,
            "jurisdiction": jurisdiction
        }, indent=2)

    async def load_precedent(self, jurisdiction: str, document_type: str, topic: str) -> str:
        """Concatenate PDF pages matching jurisdiction prefix."""
        combined: list[str] = []
        src = "Unknown"
        for pdf in self._iter_pdf_files():
            if not pdf.name.lower().startswith(jurisdiction.lower()):
                continue
            pages = self._pdf_pages(pdf)
            src = pdf.name
            combined.extend(pages)
            if len(combined) > 20:
                break

        full_text = "\n\n".join(combined)
        if len(full_text) > 2000:
            full_text = full_text[:2000] + "..."

        return json.dumps(
            {
                "document_title": f"{jurisdiction.replace('_', ' ').title()} {document_type.replace('_', ' ').title()}",
                "full_text": full_text,
                "source": src,
                "topic": topic,
                "adaptability": "requires_modification",
            },
            indent=2,
        )

    async def extract_minutes(self, document: str, search_terms: list[str], date_range: str) -> str:
        """Search a specific PDF for search_terms."""
        pdf_path = self.docs_path / document
        if not pdf_path.exists():
            return json.dumps(
                {"document": document, "matches": [], "date_range": date_range, "error": "not found"},
                indent=2,
            )

        pages = self._pdf_pages(pdf_path)
        matches: list[dict[str, Any]] = []
        for term in search_terms:
            lt = term.lower().strip()
            if not lt:
                continue
            for idx, page_text in enumerate(pages):
                hay = page_text.lower()
                pos = hay.find(lt)
                if pos == -1:
                    continue
                matches.append(
                    {
                        "search_term": term,
                        "page": idx + 1,
                        "context": self._make_snippet(page_text, pos, pos + len(term)),
                    }
                )
                if len(matches) >= 10:
                    break
            if len(matches) >= 10:
                break

        return json.dumps({"document": document, "matches": matches, "date_range": date_range}, indent=2)

    async def load_resource(self, uri: str) -> str:
        """Load full text of all PDFs or a single PDF."""
        name = uri.split("/")[-1].strip()
        if name and name.lower() not in ("docs", "documents"):
            pdf_path = self.docs_path / name
            if pdf_path.exists() and pdf_path.suffix.lower() == ".pdf":
                return "\n\n".join(self._pdf_pages(pdf_path))

        all_text: list[str] = []
        for pdf in self._iter_pdf_files():
            all_text.extend(self._pdf_pages(pdf))
        return "\n\n".join(all_text)
