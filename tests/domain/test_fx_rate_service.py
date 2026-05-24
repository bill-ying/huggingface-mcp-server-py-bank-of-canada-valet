"""
Tests for FxRateService (Facade).

Uses a MockRateProvider (Strategy) for deterministic testing
without network calls.
"""

import pytest

from mcp_server_bank_of_canada.domain.types import Currency
from mcp_server_bank_of_canada.domain.fx_rate_service import FxRateService
from tests.conftest import create_mock_provider, MockRateProvider


class TestFxRateService:
    """Test suite for FxRateService."""

    def setup_method(self) -> None:
        self.provider = create_mock_provider()
        self.service = FxRateService(self.provider)

    async def test_usd_to_cad_rate(self) -> None:
        """Should return rate for USD to CAD on a valid date."""
        result = await self.service.get_rate_for_date(
            Currency.USD, Currency.CAD, "2024-01-15"
        )
        assert result is not None
        assert result.rate == 1.3456
        assert result.from_currency == Currency.USD
        assert result.to_currency == Currency.CAD
        assert result.rate_date == "2024-01-15"

    async def test_cad_to_usd_rate(self) -> None:
        """Should return rate for CAD to USD."""
        result = await self.service.get_rate_for_date(
            Currency.CAD, Currency.USD, "2024-01-15"
        )
        assert result is not None
        assert result.rate == 0.7432
        assert result.from_currency == Currency.CAD
        assert result.to_currency == Currency.USD

    async def test_converted_amount(self) -> None:
        """Should calculate converted amount when amount is provided."""
        result = await self.service.get_rate_for_date(
            Currency.USD, Currency.CAD, "2024-01-15", amount=100
        )
        assert result is not None
        assert result.amount == 100
        assert result.converted_amount == 134.56

    async def test_no_amount_returns_none_converted(self) -> None:
        """Should not include converted_amount when amount is not provided."""
        result = await self.service.get_rate_for_date(
            Currency.USD, Currency.CAD, "2024-01-15"
        )
        assert result is not None
        assert result.amount is None
        assert result.converted_amount is None

    async def test_missing_date_returns_none(self) -> None:
        """Should return None for dates with no data."""
        result = await self.service.get_rate_for_date(
            Currency.USD, Currency.CAD, "2024-12-25"
        )
        assert result is None

    async def test_unsupported_currency_pair_raises(self) -> None:
        """Should raise ValueError for unsupported currency pairs."""
        with pytest.raises(ValueError, match="Unsupported currency pair: EUR to CAD"):
            await self.service.get_rate_for_date(
                "EUR", Currency.CAD, "2024-01-15"  # type: ignore[arg-type]
            )

    async def test_same_currency_raises(self) -> None:
        """Should raise ValueError for same-currency pairs."""
        with pytest.raises(ValueError, match="Unsupported currency pair: USD to USD"):
            await self.service.get_rate_for_date(
                Currency.USD, Currency.USD, "2024-01-15"
            )

    async def test_result_is_frozen(self) -> None:
        """Should return a frozen (immutable) result."""
        result = await self.service.get_rate_for_date(
            Currency.USD, Currency.CAD, "2024-01-15"
        )
        assert result is not None
        with pytest.raises(Exception):
            result.rate = 999.0  # type: ignore[misc]

    async def test_malformed_rate_returns_none(self) -> None:
        """Should return None when the rate value is not a valid number."""
        provider = MockRateProvider([
            (
                "FXUSDCAD:2024-01-15",
                [{"d": "2024-01-15", "FXUSDCAD": {"v": "not-a-number"}}],
            ),
        ])
        service = FxRateService(provider)
        result = await service.get_rate_for_date(
            Currency.USD, Currency.CAD, "2024-01-15"
        )
        assert result is None

    async def test_missing_series_key_returns_none(self) -> None:
        """Should return None when the observation lacks the expected series key."""
        provider = MockRateProvider([
            (
                "FXUSDCAD:2024-01-15",
                [{"d": "2024-01-15"}],  # no FXUSDCAD key
            ),
        ])
        service = FxRateService(provider)
        result = await service.get_rate_for_date(
            Currency.USD, Currency.CAD, "2024-01-15"
        )
        assert result is None

