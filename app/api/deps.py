from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_session
from app.infrastructure.repositories.price import PriceRepositoryImpl
from app.domain.services.price import PriceService


def get_price_service(
    session: AsyncSession = Depends(get_session),
) -> PriceService:
    repo = PriceRepositoryImpl(session)
    return PriceService(repo)
