"""
get_rate_tool — Idiomatic Python Tool function.

Exposes a functional interface for fetching exchange rates.
This is meant to be registered with FastMCP via @mcp.tool().
"""

from typing import Optional

from ..domain.types import Currency, ExchangeResult
from ..domain.fx_rate_service import FxRateService


async def get_rate(
    service: FxRateService,
    from_currency: Currency,
    to_currency: Currency,
    date: str,
    amount: Optional[float] = None,
) -> str:
    """
    Get the exchange rate between USD and CAD for a specific date from Bank of Canada.

    Args:
        from_currency: Source currency (USD or CAD)
        to_currency: Target currency (USD or CAD)
        date: Date in YYYY-MM-DD format
        amount: Optional amount to convert
    """
    result = await service.get_rate_for_date(
        from_currency,
        to_currency,
        date,
        amount,
    )

    if not result:
        return "No exchange rate data available for that date."

    text = (
        f"Exchange rate on {result.rate_date}: "
        f"1 {result.from_currency.value} = {result.rate} {result.to_currency.value}"
    )
    if result.amount is not None and result.converted_amount is not None:
        text += (
            f"\n{result.amount} {result.from_currency.value} "
            f"= {result.converted_amount} {result.to_currency.value}"
        )

    return text
