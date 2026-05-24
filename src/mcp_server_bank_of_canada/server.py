"""
MCP Server Entry Point.

Uses FastMCP — the standard Python MCP SDK — to serve a
stateless MCP server over SSE or stdio transport.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .providers.bank_of_canada_provider import BankOfCanadaProvider
from .domain.fx_rate_service import FxRateService
from .domain.types import Currency
from .tools.get_rate_tool import get_rate


def create_server() -> FastMCP:
    """
    Factory: Creates a fully-wired FastMCP server instance.
    """
    mcp = FastMCP(
        "bank-of-canada-mcp",
        host="0.0.0.0",
        instructions=(
            "MCP server providing Bank of Canada exchange rates. "
            "Use the get_rate tool to fetch USD/CAD rates for a specific date."
        ),
    )

    provider = BankOfCanadaProvider()
    service = FxRateService(provider)

    @mcp.tool()
    async def get_exchange_rate(
        from_currency: Currency = Field(description="Source currency (USD or CAD)"),
        to_currency: Currency = Field(description="Target currency (USD or CAD)"),
        date: str = Field(description="Date in YYYY-MM-DD format"),
        amount: float | None = Field(default=None, description="Optional amount to convert"),
    ) -> str:
        """Get the exchange rate between USD and CAD for a specific date from Bank of Canada."""
        return await get_rate(service, from_currency, to_currency, date, amount)

    return mcp


# Module-level server instance for uvicorn / CLI usage
mcp = create_server()

# ASGI app for Docker / Cloud Run deployment (uvicorn target)
app = mcp.sse_app()
