"""
Tests for BankOfCanadaProvider (Concrete Strategy).

Uses pytest-httpx to intercept outbound HTTP requests for deterministic,
readable testing without brittle mock-patch chains.
"""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from mcp_server_bank_of_canada.providers.bank_of_canada_provider import (
    BankOfCanadaProvider,
)

BASE_URL = "https://www.bankofcanada.ca/valet/observations"


class TestBankOfCanadaProvider:
    """Test suite for BankOfCanadaProvider."""

    def setup_method(self) -> None:
        self.provider = BankOfCanadaProvider()

    async def test_constructs_correct_url(self, httpx_mock: HTTPXMock) -> None:
        """Should construct the correct URL with series name and date params."""
        httpx_mock.add_response(
            url=f"{BASE_URL}/FXUSDCAD/json?start_date=2024-01-15&end_date=2024-01-15",
            json={"observations": [{"d": "2024-01-15", "FXUSDCAD": {"v": "1.35"}}]},
        )

        await self.provider.get_observations("FXUSDCAD", "2024-01-15", "2024-01-15")

        # pytest-httpx asserts that all registered mocks were called
        requests = httpx_mock.get_requests()
        assert len(requests) == 1
        assert "FXUSDCAD/json" in str(requests[0].url)
        assert requests[0].url.params["start_date"] == "2024-01-15"
        assert requests[0].url.params["end_date"] == "2024-01-15"

    async def test_returns_observations(self, httpx_mock: HTTPXMock) -> None:
        """Should return observations from a valid API response."""
        expected = [{"d": "2024-01-15", "FXUSDCAD": {"v": "1.3456"}}]
        httpx_mock.add_response(
            url=f"{BASE_URL}/FXUSDCAD/json?start_date=2024-01-15",
            json={"observations": expected},
        )

        result = await self.provider.get_observations("FXUSDCAD", "2024-01-15")
        assert result == expected

    async def test_returns_empty_when_no_observations(self, httpx_mock: HTTPXMock) -> None:
        """Should return empty list when no observations key exists."""
        httpx_mock.add_response(
            url=f"{BASE_URL}/FXUSDCAD/json?start_date=2099-01-01",
            json={},
        )

        result = await self.provider.get_observations("FXUSDCAD", "2099-01-01")
        assert result == []

    async def test_raises_on_error_status(self, httpx_mock: HTTPXMock) -> None:
        """Should raise HTTPStatusError on non-2xx response."""
        httpx_mock.add_response(
            url=f"{BASE_URL}/FXUSDCAD/json?start_date=2024-01-15",
            status_code=500,
        )

        with pytest.raises(httpx.HTTPStatusError):
            await self.provider.get_observations("FXUSDCAD", "2024-01-15")

    async def test_omits_date_params_when_not_provided(self, httpx_mock: HTTPXMock) -> None:
        """Should not include date params when start_date is omitted."""
        httpx_mock.add_response(
            url=f"{BASE_URL}/FXUSDCAD/json",
            json={"observations": []},
        )

        await self.provider.get_observations("FXUSDCAD")

        requests = httpx_mock.get_requests()
        assert "start_date" not in requests[0].url.params
        assert "end_date" not in requests[0].url.params
