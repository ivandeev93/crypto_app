import time
import asyncio

from app.core.celery_app import celery_app
from app.infrastructure.clients.deribit import DeribitClient
from app.domain.entities.price import PriceRecord
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.repositories.price import PriceRepositoryImpl
from app.domain.services.price import PriceService

TICKERS = ("btc_usd", "eth_usd")

@celery_app.task
def fetch_prices():
    asyncio.run(_fetch_prices())


async def _fetch_prices():
    session = AsyncSessionLocal()
    try:
        repo = PriceRepositoryImpl(session)
        service = PriceService(repo)
        client = DeribitClient()

        timestamp = int(time.time())

        for ticker in TICKERS:
            price = await client.get_index_price(ticker)
            record = PriceRecord(
                ticker=ticker,
                price=price,
                timestamp=timestamp,
            )
            await service.save_price(record)
    finally:
        await session.close()
