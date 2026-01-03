\
from __future__ import annotations

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


Color = Literal["GREEN", "YELLOW", "RED"]
YesNoUnknown = Literal["YES", "NO", "UNKNOWN"]
StaffHours = Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
LegalAuthority = Literal["YES", "NO", "REQUIRES_COUNSEL_REVIEW"]


class Citation(BaseModel):
    document_id: str
    document: Optional[str] = None
    url: Optional[str] = None
    out_path: Optional[str] = None
    published_at: Optional[str] = None
    fetched_at: Optional[str] = None
    location: Optional[str] = Field(
        default=None,
        description="Location hint for validation (offset range or page if known).",
    )


class Fact(BaseModel):
    color: Color
    claim: str
    citation: Optional[Citation] = None
    support: Optional[list[Citation]] = None
    notes: Optional[str] = None


class IngestSourcesRequest(BaseModel):
    records_jsonl_path: str = Field(description="Path to records.jsonl")
    reddit_jsonl_path: Optional[str] = Field(default=None, description="Optional path to reddit.jsonl")
    replace_existing: bool = False


class IngestSourcesResponse(BaseModel):
    documents_ingested: int
    reddit_items_ingested: int


class SearchRequest(BaseModel):
    q: str = Field(description="Search string")
    limit: int = 20


class SearchHit(BaseModel):
    document_id: str
    title: Optional[str] = None
    url: Optional[str] = None
    out_path: Optional[str] = None
    snippet: str
    score: float
    citation: Citation


class SearchResponse(BaseModel):
    q: str
    hits: list[SearchHit]


class ExtractFactsRequest(BaseModel):
    document_id: str
    search_terms: list[str] = Field(default_factory=list)
    max_snippets: int = 10


class ExtractFactsResponse(BaseModel):
    document_id: str
    facts: list[Fact]
    red_items: list[str]


class ValidateCitationRequest(BaseModel):
    document_id: str
    claimed_text: str
    max_context_chars: int = 220


class ValidateCitationResponse(BaseModel):
    status: Literal["valid", "not_found", "mismatch", "error"]
    document_id: str
    matches: int = 0
    contexts: list[str] = Field(default_factory=list)


class FeasibilityRequest(BaseModel):
    proposed_control: str
    jurisdiction: Literal["elpaso", "dona_ana"]
    utility_type: Literal["water", "electric", "gas"]


class FeasibilityResponse(BaseModel):
    can_export_this_format: YesNoUnknown
    can_ingest_with_existing_tools: YesNoUnknown
    estimated_staff_hours: StaffHours
    legal_authority_confirmed: LegalAuthority
    warnings: list[str] = Field(default_factory=list)


class RecordsRequestInput(BaseModel):
    jurisdiction: Literal["city_of_elpaso", "epwater", "dona_ana_county"]
    records_custodian: Optional[str] = None
    date_range: str = Field(description="YYYY-MM-DD to YYYY-MM-DD")
    specific_topic: str
    red_items: list[str] = Field(default_factory=list)


class RecordsRequestOutput(BaseModel):
    template_markdown: str
    red_items_included: int


class HealthResponse(BaseModel):
    ok: bool
    db_path: str
    documents: int
