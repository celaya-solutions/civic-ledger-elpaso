\
from __future__ import annotations

from .models import ValidateCitationResponse


def validate_exact_substring(*, document_id: str, text: str, claimed_text: str, max_context_chars: int) -> ValidateCitationResponse:
    try:
        if not claimed_text or not claimed_text.strip():
            return ValidateCitationResponse(status="error", document_id=document_id, matches=0, contexts=["claimed_text is empty"])

        hay = (text or "")
        needle = claimed_text.strip()

        idx = 0
        matches = 0
        contexts: list[str] = []
        while True:
            pos = hay.find(needle, idx)
            if pos == -1:
                break
            matches += 1
            a = max(0, pos - max_context_chars)
            b = min(len(hay), pos + len(needle) + max_context_chars)
            contexts.append(hay[a:b].replace("\n", " ").strip())
            idx = pos + len(needle)
            if len(contexts) >= 5:
                break

        if matches == 0:
            return ValidateCitationResponse(status="not_found", document_id=document_id, matches=0, contexts=[])

        return ValidateCitationResponse(status="valid", document_id=document_id, matches=matches, contexts=contexts)

    except Exception as e:
        return ValidateCitationResponse(status="error", document_id=document_id, matches=0, contexts=[str(e)])
