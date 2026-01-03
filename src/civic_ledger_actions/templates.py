\
from __future__ import annotations

from datetime import date
from .models import RecordsRequestOutput


def generate_records_request_markdown(*, jurisdiction: str, records_custodian: str | None, date_range: str, specific_topic: str, red_items: list[str]) -> RecordsRequestOutput:
    today = date.today().isoformat()
    custodian = records_custodian or "Records Custodian"

    items_block = ""
    if red_items:
        items_block = "\n".join([f"- {x}" for x in red_items])
    else:
        items_block = "- (none provided)"

    md = f"""\
Request date: {today}

To: {custodian}
Jurisdiction target: {jurisdiction}

Subject: Public records request regarding: {specific_topic}

Date range:
- {date_range}

Requested records:
{items_block}

Delivery format requested:
- Electronic copies (PDF where applicable)
- If available, machine-readable exports (CSV/JSON) for non-sensitive aggregates

Notes:
- This template is a technical drafting aid only. It is not legal advice.
- Submit through official records request channels.
"""
    return RecordsRequestOutput(template_markdown=md, red_items_included=len(red_items))
