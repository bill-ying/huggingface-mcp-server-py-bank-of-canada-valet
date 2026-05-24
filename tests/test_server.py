"""
Tests for the server factory (create_server).
"""

from mcp_server_bank_of_canada.server import create_server


class TestCreateServer:
    """Test suite for the create_server() factory function."""

    def test_returns_fastmcp_instance(self) -> None:
        """Should return a FastMCP instance."""
        from mcp.server.fastmcp import FastMCP

        server = create_server()
        assert isinstance(server, FastMCP)

    def test_server_has_correct_name(self) -> None:
        """Should create a server named 'bank-of-canada-mcp'."""
        server = create_server()
        assert server.name == "bank-of-canada-mcp"

    def test_get_rate_tool_is_registered(self) -> None:
        """Should register the get_exchange_rate tool."""
        server = create_server()
        # FastMCP stores tools in an internal dict keyed by name
        tool_names = list(server._tool_manager._tools.keys())
        assert "get_exchange_rate" in tool_names

    def test_each_call_returns_independent_instance(self) -> None:
        """Should return a fresh instance on each call (no shared state)."""
        server_a = create_server()
        server_b = create_server()
        assert server_a is not server_b
