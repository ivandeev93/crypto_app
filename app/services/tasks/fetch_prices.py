import asyncio
import time
from typing import List

from app.core.celery_app import celery_app
from app.infrastructure.clients.deribit import DeribitClient
from app.domain.entities.price import PriceRecord
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.repositories.price import PriceRepositoryImpl
from app.domain.services.price import PriceService

TICKERS: List[str] = ["btc_usd", "eth_usd"]


async def _fetch_prices() -> None:
    """
    Асинхронная функция для получения текущих цен и сохранения их в базу.
    """
    # Создаем сессию БД
    async with AsyncSessionLocal() as session:
        repo = PriceRepositoryImpl(session)
        service = PriceService(repo)
        client = DeribitClient()

        timestamp = int(time.time())  # фиксируем одно время для всех тикеров

        for ticker in TICKERS:
            price_value = await client.get_index_price(ticker)
            record = PriceRecord(
                ticker=ticker,
                price=price_value,
                timestamp=timestamp,
            )
            await service.save_price(record)


@celery_app.task
def fetch_prices() -> None:
    """
    Синхронная обёртка для Celery.
    Celery не поддерживает async, поэтому используем asyncio.run.
    """
    asyncio.run(_fetch_prices())
