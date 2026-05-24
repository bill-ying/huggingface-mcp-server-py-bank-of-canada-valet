"""Shared test fixtures."""

from typing import Any, Optional

from mcp_server_bank_of_canada.domain.types import RateProvider


class MockRateProvider(RateProvider):
    """
    Mock Provider — implements RateProvider Strategy for testing.

    Stores data keyed by ``{series_name}:{start_date}`` for deterministic lookups.
    """

    def __init__(self, entries: list[tuple[str, list[dict[str, Any]]]]) -> None:
        self._data: dict[str, list[dict[str, Any]]] = dict(entries)

    async def get_observations(
        self,
        series_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        key = f"{series_name}:{start_date or ''}"
        return self._data.get(key, [])


def create_mock_provider() -> MockRateProvider:
    """Create a pre-loaded mock provider with standard test data."""
    return MockRateProvider([
        (
            "FXUSDCAD:2024-01-15",
            [{"d": "2024-01-15", "FXUSDCAD": {"v": "1.3456"}}],
        ),
        (
            "FXCADUSD:2024-01-15",
            [{"d": "2024-01-15", "FXCADUSD": {"v": "0.7432"}}],
        ),
        (
            "FXUSDCAD:2024-03-01",
            [{"d": "2024-03-01", "FXUSDCAD": {"v": "1.3600"}}],
        ),
    ])
