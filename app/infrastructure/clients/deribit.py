import aiohttp
from typing import Optional
from app.core.config import settings
import logging


# Настройка логгера
logger = logging.getLogger(__name__)


class DeribitClient:
    """
    Асинхронный клиент для публичного API Deribit.
    Используется как async context manager.
    """

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url: str = settings.deribit_base_url.rstrip("/")

    async def __aenter__(self) -> "DeribitClient":
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=20,
        )
        self._session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def get_index_price(self, ticker: str) -> float:
        """
        Получает index price для указанного тикера.
        ticker: btc_usd | eth_usd
        """
        if self._session is None:
            raise RuntimeError(
                "DeribitClient must be used as an async context manager"
            )

        url = f"{self._base_url}/get_index_price"
        params = {"index_name": ticker}

        logger.info(
            "Запрос к Deribit: url=%s, index_name=%s",
            url,
            ticker,
        )

        try:
            async with self._session.get(
                    url,
                    params=params,
            ) as response:
                response.raise_for_status()
                data = await response.json()

        except (aiohttp.ClientError, TimeoutError):
            logger.exception(
                "Ошибка HTTP-запроса к Deribit для %s",
                ticker,
            )
            raise

        if "error" in data:
            raise RuntimeError(
                f"Deribit API error for {ticker}: {data['error']}"
            )

        try:
            price = float(data["result"]["index_price"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Unexpected Deribit API response for {ticker}: {data}"
            ) from exc

        logger.info(
            "Получена индексная цена Deribit: %s = %s",
            ticker,
            price,
        )

        return price
