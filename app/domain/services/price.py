from typing import List, Optional
from app.domain.entities.price import PriceRecord
from app.domain.repositories.price import PriceRepository

class PriceService:

    def __init__(self, repository: PriceRepository):
        self._repository = repository

    async def save_price(self, record: PriceRecord) -> None:
        await self._repository.add(record)

    async def get_all(self, ticker: str) -> List[PriceRecord]:
        return await self._repository.get_all(ticker)

    async def get_last(self, ticker: str) -> Optional[PriceRecord]:
        return await self._repository.get_last(ticker)

    async def get_by_date(
        self,
        ticker: str,
        date_from: int,
        date_to: int,
    ) -> List[PriceRecord]:
        return await self._repository.get_by_date(
            ticker, date_from, date_to
        )
