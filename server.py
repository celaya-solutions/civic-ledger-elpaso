"""
Civic Ledger MCP Server
Provides document search, citation validation, and policy generation for El Paso civic accountability.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, EmbeddedResource
from pydantic import BaseModel, Field

from document_loader import DocumentLoader
from citation_validator import CitationValidator
from template_generator import TemplateGenerator
from feasibility_checker import FeasibilityChecker


DOCS_PATH = Path("./docs")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("civic-ledger-mcp")


# Initialize components with defensive guards
try:
    doc_loader = DocumentLoader(docs_path=str(DOCS_PATH))
except Exception as exc:  # pragma: no cover
    logger.error("Failed to initialize DocumentLoader: %s", exc)
    doc_loader = None

citation_validator = CitationValidator(DOCS_PATH)
template_gen = TemplateGenerator()
feasibility_checker = FeasibilityChecker()

# Create server instance
server = Server("civic-ledger-mcp")


# Tool input schemas
class SearchLegalAuthorityInput(BaseModel):
    jurisdiction: str = Field(description="texas or new_mexico")
    topic: str = Field(description="development_agreements, utility_regulation, or open_records")
    query: str = Field(description="Natural language query about legal authority")


class ValidateCitationInput(BaseModel):
    document: str = Field(description="Document filename under docs/")
    page: int | None = Field(default=None, description="Page number (1-based) or null for full scan")
    section: str | None = Field(default=None, description="Optional section identifier")
    claimed_text: str = Field(description="Text that was cited")


class LoadPrecedentInput(BaseModel):
    jurisdiction: str = Field(description="loudoun_county, mesa, or raleigh_durham")
    document_type: str = Field(description="development_agreement, water_contract, or rate_structure")
    topic: str = Field(description="infrastructure_escrow, cost_allocation, or transparency")


class GenerateRecordsRequestInput(BaseModel):
    jurisdiction: str = Field(description="city_of_elpaso, epwater, or dona_ana_county")
    document_type: str = Field(description="board_minutes, development_agreement, or cost_study")
    date_range: str = Field(description="Date range in format 'YYYY-MM-DD to YYYY-MM-DD'")
    specific_topic: str = Field(description="Specific topic to request")


class CheckFeasibilityInput(BaseModel):
    proposed_control: str = Field(description="Description of proposed control/requirement")
    jurisdiction: str = Field(description="elpaso or santa_teresa")
    utility_type: str = Field(description="water, electric, or gas")


class AssemblePolicyPacketInput(BaseModel):
    packet_type: str = Field(description="council_presentation, commission_resolution, or rfp_package")
    components: list[str] = Field(description="List of components to include")
    jurisdiction: str = Field(description="city_of_elpaso or dona_ana_county")


class ExtractBoardMinutesInput(BaseModel):
    document: str = Field(description="Document filename in docs/")
    search_terms: list[str] = Field(description="Terms to search for")
    date_range: str = Field(description="Date range in format 'YYYY-MM-DD to YYYY-MM-DD'")


class CostBenefitInput(BaseModel):
    control_type: str = Field(description="cost_of_service_study, dashboard_development, or independent_audit")
    scope: str = Field(description="single_facility, all_data_centers, or system_wide")
    jurisdiction: str = Field(description="elpaso")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_legal_authority",
            description="Search Texas/New Mexico statutes for specific municipal powers and authorities",
            inputSchema=SearchLegalAuthorityInput.model_json_schema(),
        ),
        Tool(
            name="validate_citation",
            description="Verify that a cited document exists and contains the claimed text",
            inputSchema=ValidateCitationInput.model_json_schema(),
        ),
        Tool(
            name="load_comparable_precedent",
            description="Retrieve text of precedent agreements from other jurisdictions",
            inputSchema=LoadPrecedentInput.model_json_schema(),
        ),
        Tool(
            name="generate_records_request",
            description="Create targeted TX PIA or NM IPRA request with simple templating",
            inputSchema=GenerateRecordsRequestInput.model_json_schema(),
        ),
        Tool(
            name="check_feasibility",
            description="Validate operational feasibility of proposed control against basic heuristics",
            inputSchema=CheckFeasibilityInput.model_json_schema(),
        ),
        Tool(
            name="assemble_policy_packet",
            description="Combine multiple templates into a simple sign-ready packet",
            inputSchema=AssemblePolicyPacketInput.model_json_schema(),
        ),
        Tool(
            name="extract_board_minutes",
            description="Parse PDFs in docs/ for specific topics and dates",
            inputSchema=ExtractBoardMinutesInput.model_json_schema(),
        ),
        Tool(
            name="cost_benefit_calculator",
            description="Calculate fiscal impact and ROI of proposed civic controls (heuristic)",
            inputSchema=CostBenefitInput.model_json_schema(),
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    try:
        if name == "search_legal_authority":
            if not doc_loader:
                raise RuntimeError("DocumentLoader unavailable")
            result = await doc_loader.search_statutes(
                jurisdiction=arguments["jurisdiction"],
                topic=arguments["topic"],
                query=arguments["query"],
            )
            return [TextContent(type="text", text=result)]

        if name == "validate_citation":
            result = await citation_validator.validate(
                document=arguments["document"],
                page=arguments.get("page"),
                section=arguments.get("section"),
                claimed_text=arguments["claimed_text"],
            )
            return [TextContent(type="text", text=result)]

        if name == "load_comparable_precedent":
            if not doc_loader:
                raise RuntimeError("DocumentLoader unavailable")
            result = await doc_loader.load_precedent(
                jurisdiction=arguments["jurisdiction"],
                document_type=arguments["document_type"],
                topic=arguments["topic"],
            )
            return [TextContent(type="text", text=result)]

        if name == "generate_records_request":
            result = await template_gen.generate_pia_request(
                jurisdiction=arguments["jurisdiction"],
                document_type=arguments["document_type"],
                date_range=arguments["date_range"],
                specific_topic=arguments["specific_topic"],
            )
            return [TextContent(type="text", text=result)]

        if name == "check_feasibility":
            result = await feasibility_checker.check(
                proposed_control=arguments["proposed_control"],
                jurisdiction=arguments["jurisdiction"],
                utility_type=arguments["utility_type"],
            )
            return [TextContent(type="text", text=result)]

        if name == "assemble_policy_packet":
            result = await template_gen.assemble_packet(
                packet_type=arguments["packet_type"],
                components=arguments["components"],
                jurisdiction=arguments["jurisdiction"],
            )
            return [TextContent(type="text", text=result)]

        if name == "extract_board_minutes":
            if not doc_loader:
                raise RuntimeError("DocumentLoader unavailable")
            result = await doc_loader.extract_minutes(
                document=arguments["document"],
                search_terms=arguments["search_terms"],
                date_range=arguments["date_range"],
            )
            return [TextContent(type="text", text=result)]

        if name == "cost_benefit_calculator":
            result = await feasibility_checker.calculate_costs(
                control_type=arguments["control_type"],
                scope=arguments["scope"],
                jurisdiction=arguments["jurisdiction"],
            )
            return [TextContent(type="text", text=result)]

        raise ValueError(f"Unknown tool: {name}")

    except Exception as exc:  # pragma: no cover
        logger.error("Error in tool %s: %s", name, exc)
        return [TextContent(type="text", text=f"Error: {exc}")]


@server.list_resources()
async def list_resources() -> list[EmbeddedResource]:
    """List available document resources"""
    resources: list[EmbeddedResource] = []

    resources.append(EmbeddedResource(
        uri="local://docs",
        name="Local docs folder",
        description="Documents under ./docs indexed by the DocumentLoader",
        mimeType="application/pdf",
    ))
    return resources


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read full text of a resource"""
    if not doc_loader:
        raise RuntimeError("DocumentLoader unavailable")
    return await doc_loader.load_resource(uri)


async def main() -> None:
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
