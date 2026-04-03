import asyncio
import time
import logging
from typing import Iterable, List

from app.core.celery_app import celery_app
from app.domain.entities.price import PriceRecord
from app.domain.services.price import PriceService
from app.domain.entities.ticker import Ticker
from app.infrastructure.clients.deribit import DeribitClient
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.repositories.price import PriceRepositoryImpl

# Настройка логгера
logger = logging.getLogger(__name__)

# Список тикеров, берём из Enum
TICKERS: List[Ticker] = [Ticker.BTC_USD, Ticker.ETH_USD]


async def fetch_prices_async(tickers: Iterable[Ticker] = TICKERS) -> None:
    """
    Асинхронно получает текущие цены по тикерам
    и сохраняет их в БД.
    """
    timestamp = int(time.time())

    async with AsyncSessionLocal() as session:
        repository = PriceRepositoryImpl(session)
        service = PriceService(repository)

        async with DeribitClient() as client:
            for ticker in tickers:
                try:
                    price_value = await client.get_index_price(ticker.value)
                except Exception as exc:
                    logger.error("Ошибка при получении цены для %s: %s", ticker.value, exc)
                    continue

                record = PriceRecord(
                    ticker=ticker.value,
                    price=price_value,
                    timestamp=timestamp,
                )
                try:
                    await service.save_price(record)
                    logger.info("Сохранили цену %s: %s", ticker.value, price_value)
                except Exception as exc:
                    logger.error("Ошибка при сохранении цены для %s: %s", ticker.value, exc)


@celery_app.task(name="fetch_prices")
def fetch_prices() -> None:
    """
    Точка входа для Celery.
    Celery не поддерживает async-задачи напрямую,
    поэтому используем asyncio.run.
    """
    asyncio.run(fetch_prices_async())
