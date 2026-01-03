from __future__ import annotations

import json


class FeasibilityChecker:
    """Rule-of-thumb feasibility and cost calculator."""

    async def check(self, *, proposed_control: str, jurisdiction: str, utility_type: str) -> str:
        txt = (proposed_control or "").lower()
        warnings: list[str] = []
        can_export = "UNKNOWN"
        can_ingest = "UNKNOWN"
        staff_hours = "UNKNOWN"
        legal = "REQUIRES_COUNSEL_REVIEW"

        if "publish" in txt and "aggregate" in txt:
            can_export = "YES"
            can_ingest = "YES"
            staff_hours = "LOW"

        if "real-time" in txt or "hourly" in txt:
            warnings.append("Real-time publishing may increase operational burden and privacy review.")
            staff_hours = "HIGH"

        if "escrow" in txt or "clawback" in txt or "penalty" in txt:
            warnings.append("Finance controls require counsel review and contracting authority alignment.")
            legal = "REQUIRES_COUNSEL_REVIEW"
            if staff_hours == "UNKNOWN":
                staff_hours = "MEDIUM"

        return json.dumps({
            "proposed_control": proposed_control,
            "jurisdiction": jurisdiction,
            "utility_type": utility_type,
            "can_export_this_format": can_export,
            "can_ingest_with_existing_tools": can_ingest,
            "estimated_staff_hours": staff_hours,
            "legal_authority_confirmed": legal,
            "warnings": warnings,
        }, indent=2)

    async def calculate_costs(self, *, control_type: str, scope: str, jurisdiction: str) -> str:
        base = {
            "cost_of_service_study": 75000,
            "dashboard_development": 45000,
            "independent_audit": 60000,
        }.get(control_type, 50000)

        multiplier = {
            "single_facility": 1.0,
            "all_data_centers": 1.4,
            "system_wide": 1.8,
        }.get(scope, 1.0)

        estimate = int(base * multiplier)
        return json.dumps({
            "control_type": control_type,
            "scope": scope,
            "jurisdiction": jurisdiction,
            "estimated_cost_usd": estimate,
            "notes": "Estimates are heuristic and should be validated with procurement.",
        }, indent=2)
