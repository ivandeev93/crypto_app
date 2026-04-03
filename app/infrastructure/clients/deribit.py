import aiohttp
from typing import Optional

from app.core.config import settings


class DeribitClient:
    """
    Асинхронный клиент для публичного API Deribit.
    Используется как async context manager.
    """

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url: str = settings.deribit_base_url

    async def __aenter__(self) -> "DeribitClient":
        timeout = aiohttp.ClientTimeout(total=10)
        self._session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session:
            await self._session.close()

    async def get_index_price(self, ticker: str) -> float:
        """
        Получает index price для указанного тикера.
        ticker: btc_usd | eth_usd
        """
        if not self._session:
            raise RuntimeError("DeribitClient must be used as an async context manager")

        url = f"{self._base_url}/get_index_price"

        async with self._session.get(
            url,
            params={"index_name": ticker},
        ) as response:
            response.raise_for_status()
            data = await response.json()

        return float(data["result"]["index_price"])
