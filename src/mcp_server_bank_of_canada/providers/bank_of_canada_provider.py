"""
BankOfCanadaProvider — Concrete Strategy (GoF Strategy Pattern).

Implements the RateProvider interface to fetch observations from
the Bank of Canada Valet API. This provider can be swapped with
a mock or cached implementation for testing or resilience.
"""

from typing import Any, Optional

import httpx

from ..domain.types import RateProvider


class BankOfCanadaProvider(RateProvider):
    """Fetches exchange rate observations from the Bank of Canada Valet API."""

    _BASE_URL = "https://www.bankofcanada.ca/valet/observations"

    async def get_observations(
        self,
        series_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch observations from the Valet API.

        Args:
            series_name: The BoC series identifier (e.g., FXUSDCAD).
            start_date: Optional start date filter (YYYY-MM-DD).
            end_date: Optional end date filter (YYYY-MM-DD).

        Returns:
            List of raw observation dicts from the API.

        Raises:
            httpx.HTTPStatusError: If the API responds with an error status.
        """
        url = f"{self._BASE_URL}/{series_name}/json"
        params: dict[str, str] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("observations", [])
