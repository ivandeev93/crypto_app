from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.price import PriceRecord
from app.domain.repositories.price import PriceRepository
from app.infrastructure.db.models.price import PriceModel

class PriceRepositoryImpl(PriceRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, record: PriceRecord) -> None:
        model = PriceModel(
            ticker=record.ticker,
            price=record.price,
            timestamp=record.timestamp,
        )
        self._session.add(model)
        await self._session.commit()

    async def get_all(self, ticker: str) -> List[PriceRecord]:
        stmt = select(PriceModel).where(
            PriceModel.ticker == ticker
        )
        result = await self._session.execute(stmt)
        return [
            PriceRecord(
                ticker=row.ticker,
                price=row.price,
                timestamp=row.timestamp,
            )
            for row in result.scalars().all()
        ]

    async def get_last(self, ticker: str) -> Optional[PriceRecord]:
        stmt = (
            select(PriceModel)
            .where(PriceModel.ticker == ticker)
            .order_by(desc(PriceModel.timestamp))
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return PriceRecord(
            ticker=model.ticker,
            price=model.price,
            timestamp=model.timestamp,
        )

    async def get_by_date(
        self,
        ticker: str,
        date_from: int,
        date_to: int,
    ) -> List[PriceRecord]:
        stmt = (
            select(PriceModel)
            .where(
                PriceModel.ticker == ticker,
                PriceModel.timestamp >= date_from,
                PriceModel.timestamp <= date_to,
            )
            .order_by(PriceModel.timestamp)
        )
        result = await self._session.execute(stmt)

        return [
            PriceRecord(
                ticker=row.ticker,
                price=row.price,
                timestamp=row.timestamp,
            )
            for row in result.scalars().all()
        ]
