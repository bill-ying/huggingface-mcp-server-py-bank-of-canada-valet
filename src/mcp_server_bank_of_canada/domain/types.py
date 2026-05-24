"""
Domain Value Objects and Interfaces for the Bank of Canada MCP Server.

These types form the core domain model and are consumed by providers,
services, and tools throughout the application.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class Currency(str, Enum):
    """Supported currencies for exchange rate lookup."""

    USD = "USD"
    CAD = "CAD"


class ExchangeDirection(str, Enum):
    """Direction of currency exchange and corresponding Bank of Canada series name."""

    USD_TO_CAD = "FXUSDCAD"
    CAD_TO_USD = "FXCADUSD"


class ExchangeResult(BaseModel):
    """
    Value Object: Immutable result of an exchange rate lookup.
    Ideal for audit trails in regulated financial environments.

    Frozen via Pydantic config to match the TS Object.freeze() semantics.
    """

    model_config = ConfigDict(frozen=True)

    rate_date: str
    rate: float
    from_currency: Currency
    to_currency: Currency
    amount: Optional[float] = None
    converted_amount: Optional[float] = None


class RateProvider(ABC):
    """
    Strategy interface (GoF Strategy Pattern).

    Decouples the data fetching mechanism from the service layer.
    Implement this interface to swap data sources (e.g., mock, cache, live API).
    """

    @abstractmethod
    async def get_observations(
        self,
        series_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Fetch raw observations from a rate data source."""
