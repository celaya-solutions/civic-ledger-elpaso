\
from __future__ import annotations

from .models import FeasibilityResponse


def check_feasibility_rulebased(*, proposed_control: str, jurisdiction: str, utility_type: str) -> FeasibilityResponse:
    # Conservative defaults: UNKNOWN unless simple matches allow a reasonable guess.
    txt = (proposed_control or "").lower()
    warnings: list[str] = []

    can_export = "UNKNOWN"
    can_ingest = "UNKNOWN"
    staff_hours = "UNKNOWN"
    legal = "REQUIRES_COUNSEL_REVIEW"

    # Low-risk controls
    if "publish" in txt and "aggregate" in txt:
        can_export = "YES"
        can_ingest = "YES"
        staff_hours = "LOW"

    if "real-time" in txt or "hourly" in txt:
        warnings.append("Real-time or hourly publishing often increases operational burden and privacy review.")
        staff_hours = "HIGH"

    if "escrow" in txt or "clawback" in txt or "penalty" in txt:
        warnings.append("Finance controls require counsel review and alignment with local contracting authority.")
        legal = "REQUIRES_COUNSEL_REVIEW"
        staff_hours = staff_hours if staff_hours != "UNKNOWN" else "MEDIUM"

    return FeasibilityResponse(
        can_export_this_format=can_export,
        can_ingest_with_existing_tools=can_ingest,
        estimated_staff_hours=staff_hours,
        legal_authority_confirmed=legal,
        warnings=warnings,
    )
