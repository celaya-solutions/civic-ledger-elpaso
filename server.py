"""
Civic Ledger MCP Server
Provides document search, citation validation, and policy generation for El Paso civic accountability.
"""

from __future__ import annotations
import asyncio, json, logging, os, sys
from contextlib import asynccontextmanager
from io import TextIOWrapper
from pathlib import Path
from typing import Any, AsyncIterator
import anyio
from fastapi import FastAPI
from mcp.server.lowlevel.server import Server
import mcp.types as mcp_types
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.shared.message import SessionMessage
from mcp.types import EmbeddedResource, TextContent, Tool
from pydantic import BaseModel, Field

# Internal imports
from document_loader import DocumentLoader
from citation_validator import CitationValidator
from template_generator import TemplateGenerator
from feasibility_checker import FeasibilityChecker

DOCS_PATH = Path("./docs")

# Logging setup
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger("civic-ledger-mcp")

# -------------------------------
# FASTAPI APP (EXPOSES MCP TOOLS)
# -------------------------------
app = FastAPI(title="Civic Ledger MCP API", version="1.0")

# Initialize tool components
docs_path = "./docs"
validator = CitationValidator(docs_path)
loader = DocumentLoader(docs_path)
feasibility = FeasibilityChecker()
templates = TemplateGenerator()

@app.get("/")
async def root():
    return {"status": "ok", "service": "civic-ledger-mcp"}

from pydantic import BaseModel
from fastapi import Body

class ValidateCitationBody(BaseModel):
    document: str
    page: int | None = None
    section: str | None = None
    claimed_text: str

@app.post("/validate_citation")
async def validate_citation(body: ValidateCitationBody = Body(...)):
    """Validate that a citation text exists in the specified document."""
    return await validator.validate(
        document=body.document,
        page=body.page,
        section=body.section,
        claimed_text=body.claimed_text,
    )

@app.post("/check_feasibility")
async def check_feasibility(proposed_control: str, jurisdiction: str, utility_type: str):
    return await feasibility.check(proposed_control=proposed_control, jurisdiction=jurisdiction, utility_type=utility_type)

@app.post("/search_legal_authority")
async def search_legal_authority(jurisdiction: str, topic: str, query: str):
    return await loader.search_statutes(jurisdiction=jurisdiction, topic=topic, query=query)

# -------------------------------
# MCP SERVER IMPLEMENTATION
# -------------------------------
@asynccontextmanager
async def stdio_server_skip_blanks(stdin: anyio.AsyncFile[str] | None = None, stdout: anyio.AsyncFile[str] | None = None) -> AsyncIterator[
    tuple[MemoryObjectReceiveStream[mcp_types.JSONRPCMessage | Exception], MemoryObjectSendStream[mcp_types.JSONRPCMessage]]
]:
    if not stdin:
        stdin = anyio.wrap_file(TextIOWrapper(sys.stdin.buffer, encoding="utf-8"))
    if not stdout:
        stdout = anyio.wrap_file(TextIOWrapper(sys.stdout.buffer, encoding="utf-8"))

    read_stream_writer, read_stream = anyio.create_memory_object_stream(0)
    write_stream, write_stream_reader = anyio.create_memory_object_stream(0)

    async def stdin_reader():
        async with read_stream_writer:
            async for line in stdin:
                if not line.strip():
                    continue
                try:
                    message = mcp_types.JSONRPCMessage.model_validate_json(line)
                    await read_stream_writer.send(SessionMessage(message))
                except Exception as exc:
                    await read_stream_writer.send(exc)

    async def stdout_writer():
        async with write_stream_reader:
            async for session_message in write_stream_reader:
                json_out = session_message.message.model_dump_json(by_alias=True, exclude_none=True)
                await stdout.write(json_out + "\n")
                await stdout.flush()

    async with anyio.create_task_group() as tg:
        tg.start_soon(stdin_reader)
        tg.start_soon(stdout_writer)
        yield read_stream, write_stream

# MCP instance setup
server = Server("civic-ledger-mcp")
citation_validator = CitationValidator(DOCS_PATH)
template_gen = TemplateGenerator()
feasibility_checker = FeasibilityChecker()

# -------------------------------
# MAIN MCP ENTRY POINT
# -------------------------------
async def main() -> None:
    async with stdio_server_skip_blanks() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
