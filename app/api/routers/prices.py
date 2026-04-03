from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List

from app.api.schemas.price import PriceResponse
from app.api.deps import get_price_service
from app.domain.services.price import PriceService
from app.domain.entities.ticker import Ticker


router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/", response_model=List[PriceResponse])
async def get_all_prices(
    ticker: Ticker = Query(..., description="Тикер валюты (btc_usd or eth_usd)"),
    service: PriceService = Depends(get_price_service),
):
    """
    Получение всех сохранённых цен по указанной валюте.
    """
    return await service.get_all(ticker.value)


@router.get("/last", response_model=PriceResponse)
async def get_last_price(
    ticker: Ticker = Query(..., description="Тикер валюты (btc_usd or eth_usd)"),
    service: PriceService = Depends(get_price_service),
):
    """
    Получение последней цены валюты.
    """
    price = await service.get_last(ticker.value)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    return price


@router.get("/by-date", response_model=List[PriceResponse])
async def get_prices_by_date(
    ticker: Ticker = Query(..., description="Тикер валюты (btc_usd or eth_usd)"),
    date_from: int = Query(..., description="UNIX timestamp начала периода"),
    date_to: int = Query(..., description="UNIX timestamp конца периода"),
    service: PriceService = Depends(get_price_service),
):
    """
    Получение цен по валюте с фильтром по дате.
    """
    return await service.get_by_date(
        ticker=ticker.value,
        date_from=date_from,
        date_to=date_to,
    )
