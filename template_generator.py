from __future__ import annotations

import json
from datetime import date
from typing import Any


class TemplateGenerator:
    """Simple text template generator for PIA/IPRA requests and packets."""

    async def generate_pia_request(self, *, jurisdiction: str, document_type: str, date_range: str, specific_topic: str) -> str:
        today = date.today().isoformat()
        md = f"""Request date: {today}
Jurisdiction: {jurisdiction}
Document type: {document_type}
Topic: {specific_topic}
Date range: {date_range}

Requested records:
- Copies of {document_type} related to {specific_topic}
- Any amendments or appendices
- Delivery preference: electronic (PDF/CSV where possible)

Note: This draft is a technical template and not legal advice."""
        return md

    async def assemble_packet(self, *, packet_type: str, components: list[str], jurisdiction: str) -> str:
        return json.dumps({
            "packet_type": packet_type,
            "jurisdiction": jurisdiction,
            "components": components,
            "status": "draft",
        }, indent=2)
