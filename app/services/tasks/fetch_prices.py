
import asyncio
import logging
import time
from typing import Iterable, Optional, Tuple

from app.core.celery_app import celery_app
from app.domain.entities.price import PriceRecord
from app.domain.entities.ticker import Ticker
from app.domain.services.price import PriceService
from app.infrastructure.clients.deribit import DeribitClient
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.repositories.price import PriceRepositoryImpl

logger = logging.getLogger(__name__)

TICKERS: Tuple[Ticker, ...] = (
    Ticker.btc_usd,
    Ticker.eth_usd,
)


async def fetch_prices_async(
    tickers: Optional[Iterable[Ticker]] = None,
) -> None:
    """Получает цены с Deribit и сохраняет их в PostgreSQL."""
    tickers = tuple(TICKERS if tickers is None else tickers)

    if not tickers:
        logger.warning("Список тикеров пуст")
        return

    # Счетчик сохраненных цен
    saved_count = 0

    async with DeribitClient() as client:
        async with AsyncSessionLocal() as session:
            repository = PriceRepositoryImpl(session)
            service = PriceService(repository)

            for ticker in tickers:
                try:
                    price_value = await client.get_index_price(
                        ticker.value
                    )
                except Exception:
                    logger.exception(
                        "Ошибка при получении цены для %s",
                        ticker.value,
                    )
                    continue

                record = PriceRecord(
                    ticker=ticker,
                    price=price_value,
                    timestamp=int(time.time()),
                )

                try:
                    await service.save_price(record)
                    saved_count += 1

                    logger.info(
                        "Сохранена цена %s: %s",
                        ticker.value,
                        price_value,
                    )
                except Exception:
                    logger.exception(
                        "Ошибка при сохранении цены для %s",
                        ticker.value,
                    )
                    await session.rollback()
                    raise

    if saved_count == 0:
        raise RuntimeError(
            "Не удалось получить и сохранить ни одной цены"
        )


@celery_app.task(
    name="app.services.tasks.fetch_prices.fetch_prices",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
)
def fetch_prices() -> None:
    """Синхронная точка входа Celery."""
    asyncio.run(fetch_prices_async())
