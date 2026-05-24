"""
Tests for get_rate_tool function.
"""

import pytest

from mcp_server_bank_of_canada.domain.fx_rate_service import FxRateService
from mcp_server_bank_of_canada.domain.types import Currency
from mcp_server_bank_of_canada.tools.get_rate_tool import get_rate
from tests.conftest import create_mock_provider


class TestGetRateTool:
    """Test suite for get_rate tool function."""

    def setup_method(self) -> None:
        self.service = FxRateService(create_mock_provider())

    async def test_returns_formatted_rate_text(self) -> None:
        """Should return formatted rate text for valid input."""
        result = await get_rate(self.service, Currency.USD, Currency.CAD, "2024-01-15")
        assert "1.3456" in result
        assert "2024-01-15" in result

    async def test_includes_conversion_with_amount(self) -> None:
        """Should include conversion when amount is provided."""
        result = await get_rate(self.service, Currency.USD, Currency.CAD, "2024-01-15", 250)
        assert "250.0 USD = 336.4 CAD" in result

    async def test_no_data_message(self) -> None:
        """Should return 'no data' message for missing dates."""
        result = await get_rate(self.service, Currency.USD, Currency.CAD, "2024-12-25")
        assert "No exchange rate data" in result
