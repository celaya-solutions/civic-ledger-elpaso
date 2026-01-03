\
from __future__ import annotations

import argparse
from pathlib import Path

import orjson
from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse

from .models import (
    HealthResponse,
    IngestSourcesRequest,
    IngestSourcesResponse,
    SearchRequest,
    SearchResponse,
    SearchHit,
    ExtractFactsRequest,
    ExtractFactsResponse,
    ValidateCitationRequest,
    ValidateCitationResponse,
    FeasibilityRequest,
    FeasibilityResponse,
    RecordsRequestInput,
    RecordsRequestOutput,
    Citation,
)
from .storage import DB, upsert_documents, insert_reddit_items, count_documents
from .indexer import iter_jsonl
from .extract import extract_facts_from_text
from .citations import validate_exact_substring
from .feasibility import check_feasibility_rulebased
from .templates import generate_records_request_markdown


def create_app(db_path: Path) -> FastAPI:
    db = DB(db_path)
    db.init()

    app = FastAPI(
        title="Civic Ledger Actions",
        version="0.1.0",
        default_response_class=ORJSONResponse,
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(ok=True, db_path=str(db.path), documents=count_documents(db))

    @app.post("/ingest_sources", response_model=IngestSourcesResponse)
    def ingest_sources(req: IngestSourcesRequest) -> IngestSourcesResponse:
        records_path = Path(req.records_jsonl_path)
        if not records_path.exists():
            raise HTTPException(status_code=400, detail="records_jsonl_path does not exist")

        docs_ingested = upsert_documents(db, iter_jsonl(records_path), replace_existing=req.replace_existing)

        reddit_ingested = 0
        if req.reddit_jsonl_path:
            rp = Path(req.reddit_jsonl_path)
            if rp.exists():
                reddit_ingested = insert_reddit_items(db, iter_jsonl(rp))

        return IngestSourcesResponse(documents_ingested=docs_ingested, reddit_items_ingested=reddit_ingested)

    @app.post("/search_documents", response_model=SearchResponse)
    def search_documents(req: SearchRequest) -> SearchResponse:
        q = req.q.strip()
        if not q:
            raise HTTPException(status_code=400, detail="q is empty")

        with db.connect() as conn:
            rows = conn.execute(
                """
                SELECT document_id, title, url, out_path, text, published_at, fetched_at
                FROM documents
                WHERE text LIKE ?
                LIMIT ?
                """,
                (f"%{q}%", int(req.limit)),
            ).fetchall()

        hits: list[SearchHit] = []
        for r in rows:
            text = r["text"] or ""
            pos = text.lower().find(q.lower())
            if pos == -1:
                continue
            a = max(0, pos - 140)
            b = min(len(text), pos + len(q) + 140)
            snippet = text[a:b].replace("\n", " ").strip()

            citation = Citation(
                document_id=r["document_id"],
                document=r["title"],
                url=r["url"],
                out_path=r["out_path"],
                published_at=r["published_at"],
                fetched_at=r["fetched_at"],
                location=f"offset:{pos}-{pos+len(q)}",
            )
            hits.append(SearchHit(
                document_id=r["document_id"],
                title=r["title"],
                url=r["url"],
                out_path=r["out_path"],
                snippet=snippet,
                score=1.0,
                citation=citation,
            ))

        return SearchResponse(q=q, hits=hits)

    @app.post("/extract_facts", response_model=ExtractFactsResponse)
    def extract_facts(req: ExtractFactsRequest) -> ExtractFactsResponse:
        with db.connect() as conn:
            r = conn.execute(
                """
                SELECT document_id, title, url, out_path, published_at, fetched_at, text
                FROM documents
                WHERE document_id = ?
                """,
                (req.document_id,),
            ).fetchone()

        if not r:
            raise HTTPException(status_code=404, detail="document_id not found")

        facts, red = extract_facts_from_text(
            document_id=r["document_id"],
            text=r["text"] or "",
            url=r["url"],
            out_path=r["out_path"],
            title=r["title"],
            published_at=r["published_at"],
            fetched_at=r["fetched_at"],
            search_terms=req.search_terms,
            max_snippets=req.max_snippets,
        )
        return ExtractFactsResponse(document_id=req.document_id, facts=facts, red_items=red)

    @app.post("/validate_citation", response_model=ValidateCitationResponse)
    def validate_citation(req: ValidateCitationRequest) -> ValidateCitationResponse:
        with db.connect() as conn:
            r = conn.execute("SELECT text FROM documents WHERE document_id = ?", (req.document_id,)).fetchone()
        if not r:
            raise HTTPException(status_code=404, detail="document_id not found")
        return validate_exact_substring(
            document_id=req.document_id,
            text=r["text"] or "",
            claimed_text=req.claimed_text,
            max_context_chars=req.max_context_chars,
        )

    @app.post("/check_feasibility", response_model=FeasibilityResponse)
    def check_feasibility(req: FeasibilityRequest) -> FeasibilityResponse:
        return check_feasibility_rulebased(
            proposed_control=req.proposed_control,
            jurisdiction=req.jurisdiction,
            utility_type=req.utility_type,
        )

    @app.post("/generate_records_request", response_model=RecordsRequestOutput)
    def generate_records_request(req: RecordsRequestInput) -> RecordsRequestOutput:
        return generate_records_request_markdown(
            jurisdiction=req.jurisdiction,
            records_custodian=req.records_custodian,
            date_range=req.date_range,
            specific_topic=req.specific_topic,
            red_items=req.red_items,
        )

    return app


def cli() -> None:
    import uvicorn

    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True, help="Path to sqlite db")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", default="8787")
    args = p.parse_args()

    app = create_app(Path(args.db))
    uvicorn.run(app, host=args.host, port=int(args.port))


if __name__ == "__main__":
    cli()
