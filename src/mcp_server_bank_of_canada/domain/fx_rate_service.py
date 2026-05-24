"""
FxRateService — Facade Pattern (GoF).

Provides a simplified, deterministic interface for all exchange rate
operations. Orchestrates the RateProvider strategy and encapsulates
business logic such as direction resolution, rate extraction, and
currency conversion.
"""

from typing import Optional

from .types import Currency, ExchangeDirection, ExchangeResult, RateProvider


class FxRateService:
    """Facade that coordinates rate lookups across providers."""

    def __init__(self, provider: RateProvider) -> None:
        self._provider = provider

    async def get_rate_for_date(
        self,
        from_currency: Currency,
        to_currency: Currency,
        date: str,
        amount: Optional[float] = None,
    ) -> Optional[ExchangeResult]:
        """
        Get exchange rate for a specific date with optional amount conversion.

        Args:
            from_currency: Source currency.
            to_currency: Target currency.
            date: Date in YYYY-MM-DD format.
            amount: Optional amount to convert.

        Returns:
            Frozen ExchangeResult value object, or None if no data found.
        """
        direction = self._resolve_direction(from_currency, to_currency)
        observations = await self._provider.get_observations(
            direction.value, date, date
        )

        obs = next((o for o in observations if o.get("d") == date), None)
        if not obs:
            return None

        rate = self._extract_rate(obs, direction.value)
        if rate is None:
            return None

        converted_amount = None
        if amount is not None:
            converted_amount = round(amount * rate, 4)

        return ExchangeResult(
            rate_date=date,
            rate=rate,
            from_currency=from_currency,
            to_currency=to_currency,
            amount=amount,
            converted_amount=converted_amount,
        )

    @staticmethod
    def _resolve_direction(
        from_currency: Currency, to_currency: Currency
    ) -> ExchangeDirection:
        """Resolve the exchange direction enum from a currency pair."""
        if from_currency == Currency.USD and to_currency == Currency.CAD:
            return ExchangeDirection.USD_TO_CAD
        if from_currency == Currency.CAD and to_currency == Currency.USD:
            return ExchangeDirection.CAD_TO_USD
        from_val = getattr(from_currency, "value", from_currency)
        to_val = getattr(to_currency, "value", to_currency)
        raise ValueError(
            f"Unsupported currency pair: {from_val} to {to_val}"
        )

    @staticmethod
    def _extract_rate(obs: dict, series_name: str) -> Optional[float]:
        """Extract the numeric rate from a Bank of Canada observation."""
        data = obs.get(series_name)
        if data and isinstance(data, dict) and "v" in data:
            try:
                return float(data["v"])
            except (ValueError, TypeError):
                return None
        return None
