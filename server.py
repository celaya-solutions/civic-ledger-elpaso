"""
Civic Ledger MCP Actions API
Production-ready FastAPI server matching OpenAPI 3.1.0 spec
"""

from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Internal imports
from document_loader import DocumentLoader
from citation_validator import CitationValidator
from template_generator import TemplateGenerator
from feasibility_checker import FeasibilityChecker

# Configuration
DOCS_PATH = Path("./docs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Logging setup
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger("civic-ledger-api")

# -------------------------------
# PYDANTIC MODELS (Match OpenAPI)
# -------------------------------

class TextResult(BaseModel):
    """Standard success response"""
    result: str = Field(..., description="Tool output as plain text")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None


# Input Models
class SearchLegalAuthorityInput(BaseModel):
    jurisdiction: str = Field(..., pattern="^(texas|new_mexico)$")
    topic: str = Field(..., pattern="^(development_agreements|utility_regulation|open_records)$")
    query: str


class ValidateCitationInput(BaseModel):
    document: str
    page: Optional[int] = None
    section: Optional[str] = None
    claimed_text: str


class LoadPrecedentInput(BaseModel):
    jurisdiction: str = Field(..., pattern="^(loudoun_county|mesa|raleigh_durham)$")
    document_type: str = Field(..., pattern="^(development_agreement|water_contract|rate_structure)$")
    topic: str = Field(..., pattern="^(infrastructure_escrow|cost_allocation|transparency)$")


class GenerateRecordsRequestInput(BaseModel):
    jurisdiction: str = Field(..., pattern="^(city_of_elpaso|epwater|dona_ana_county)$")
    document_type: str = Field(..., pattern="^(board_minutes|development_agreement|cost_study)$")
    date_range: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2}$")
    specific_topic: str


class CheckFeasibilityInput(BaseModel):
    proposed_control: str
    jurisdiction: str = Field(..., pattern="^(elpaso|santa_teresa)$")
    utility_type: str = Field(..., pattern="^(water|electric|gas)$")


class AssemblePolicyPacketInput(BaseModel):
    packet_type: str = Field(..., pattern="^(council_presentation|commission_resolution|rfp_package)$")
    components: list[str]
    jurisdiction: str = Field(..., pattern="^(city_of_elpaso|dona_ana_county)$")


class ExtractBoardMinutesInput(BaseModel):
    document: str
    search_terms: list[str]
    date_range: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}\s+to\s+\d{4}-\d{2}-\d{2}$")


class CostBenefitInput(BaseModel):
    control_type: str = Field(..., pattern="^(cost_of_service_study|dashboard_development|independent_audit)$")
    scope: str = Field(..., pattern="^(single_facility|all_data_centers|system_wide)$")
    jurisdiction: str = Field(..., pattern="^elpaso$")


# -------------------------------
# FASTAPI APP
# -------------------------------

app = FastAPI(
    title="Civic Ledger MCP Actions API",
    version="1.0.0",
    description=(
        "Provides document search, citation validation, and policy generation for El Paso civic accountability. "
        "Safety boundaries: no unauthorized access, no device-level meter access, no PII harvesting, no harassment."
    ),
    servers=[
        {"url": "https://civic-ledger-elpaso.fly.dev", "description": "Production"},
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # CustomGPT needs access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tool components
try:
    validator = CitationValidator(DOCS_PATH)
    feasibility = FeasibilityChecker()
    templates = TemplateGenerator()
    loader = DocumentLoader(DOCS_PATH)
    logger.info(f"✓ Initialized components with docs_path={DOCS_PATH}")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    raise


# -------------------------------
# ENDPOINTS (Match OpenAPI spec)
# -------------------------------

@app.get("/health", tags=["Feasibility"])
async def health_check():
    """Health check endpoint"""
    return {"ok": True}


@app.get("/", tags=["Feasibility"])
async def root():
    """Root endpoint for basic health"""
    return {"status": "ok", "service": "civic-ledger-mcp"}


@app.post("/legal/search", tags=["Legal Authority"], response_model=TextResult)
async def search_legal_authority(body: SearchLegalAuthorityInput = Body(...)):
    """Search TX/NM statutes for municipal powers and authorities"""
    try:
        result = await loader.search_statutes(
            jurisdiction=body.jurisdiction,
            topic=body.topic,
            query=body.query
        )
        return TextResult(result=result)
    except Exception as e:
        logger.error(f"search_legal_authority error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/citations/validate", tags=["Citations"], response_model=TextResult)
async def validate_citation(body: ValidateCitationInput = Body(...)):
    """Verify a cited document exists and contains the claimed text"""
    try:
        result = await validator.validate(
            document=body.document,
            page=body.page,
            section=body.section,
            claimed_text=body.claimed_text,
        )
        # Convert structured result to text format
        if isinstance(result, dict):
            confidence = result.get("confidence", "UNKNOWN")
            citations = result.get("citations", [])
            
            if not citations:
                text = f"[{confidence}] No matches found for: {body.claimed_text}"
            else:
                matches = []
                for cite in citations:
                    match_type = cite.get("match_type", "unknown")
                    similarity = cite.get("similarity", 0)
                    page = cite.get("page", "?")
                    matches.append(f"  - {match_type.upper()} match (similarity: {similarity:.2f}) on page {page}")
                
                text = f"[{confidence}] Found {len(citations)} match(es):\n" + "\n".join(matches)
            
            return TextResult(result=text)
        
        return TextResult(result=str(result))
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {body.document}")
    except Exception as e:
        logger.error(f"validate_citation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/precedents/load", tags=["Precedents"], response_model=TextResult)
async def load_comparable_precedent(body: LoadPrecedentInput = Body(...)):
    """Retrieve precedent agreement language from comparable jurisdictions"""
    try:
        result = await loader.load_precedent(
            jurisdiction=body.jurisdiction,
            document_type=body.document_type,
            topic=body.topic
        )
        return TextResult(result=result)
    except Exception as e:
        logger.error(f"load_comparable_precedent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/records-request/generate", tags=["Records Requests"], response_model=TextResult)
async def generate_records_request(body: GenerateRecordsRequestInput = Body(...)):
    """Generate TX PIA / NM IPRA records request template"""
    try:
        result = await templates.generate_records_request(
            jurisdiction=body.jurisdiction,
            document_type=body.document_type,
            date_range=body.date_range,
            specific_topic=body.specific_topic
        )
        return TextResult(result=result)
    except Exception as e:
        logger.error(f"generate_records_request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feasibility/check", tags=["Feasibility"], response_model=TextResult)
async def check_feasibility(body: CheckFeasibilityInput = Body(...)):
    """Check operational feasibility of a proposed control (heuristic)"""
    try:
        result = await feasibility.check(
            proposed_control=body.proposed_control,
            jurisdiction=body.jurisdiction,
            utility_type=body.utility_type
        )
        return TextResult(result=result)
    except Exception as e:
        logger.error(f"check_feasibility error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/policy-packet/assemble", tags=["Policy Packets"], response_model=TextResult)
async def assemble_policy_packet(body: AssemblePolicyPacketInput = Body(...)):
    """Assemble a sign-ready packet from templates"""
    try:
        result = await templates.assemble_packet(
            packet_type=body.packet_type,
            components=body.components,
            jurisdiction=body.jurisdiction
        )
        return TextResult(result=result)
    except Exception as e:
        logger.error(f"assemble_policy_packet error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/board-minutes/extract", tags=["Board Minutes"], response_model=TextResult)
async def extract_board_minutes(body: ExtractBoardMinutesInput = Body(...)):
    """Parse board-minutes PDFs for terms and date range"""
    try:
        result = await loader.extract_minutes(
            document=body.document,
            search_terms=body.search_terms,
            date_range=body.date_range
        )
        return TextResult(result=result)
    except Exception as e:
        logger.error(f"extract_board_minutes error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cost-benefit/calculate", tags=["Cost Benefit"], response_model=TextResult)
async def cost_benefit_calculator(body: CostBenefitInput = Body(...)):
    """Heuristic ROI / fiscal impact calculator for proposed controls"""
    try:
        result = await feasibility.calculate_cost_benefit(
            control_type=body.control_type,
            scope=body.scope,
            jurisdiction=body.jurisdiction
        )
        return TextResult(result=result)
    except Exception as e:
        logger.error(f"cost_benefit_calculator error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# STARTUP/SHUTDOWN
# -------------------------------

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Civic Ledger API starting up")
    logger.info(f"   Docs path: {DOCS_PATH.absolute()}")
    logger.info(f"   Docs exist: {DOCS_PATH.exists()}")
    if DOCS_PATH.exists():
        docs_files = list(DOCS_PATH.glob("*.md")) + list(DOCS_PATH.glob("*.pdf"))
        logger.info(f"   Found {len(docs_files)} documents")
        for doc in docs_files[:5]:  # Show first 5
            logger.info(f"     - {doc.name}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Civic Ledger API shutting down")


# -------------------------------
# DEVELOPMENT SERVER
# -------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server_complete:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
