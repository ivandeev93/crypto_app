from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.schemas.price import PriceResponse
from app.api.deps import get_price_service
from app.domain.services.price import PriceService


router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/", response_model=list[PriceResponse])
async def get_all_prices(
    ticker: str = Query(..., description="Currency ticker"),
    service: PriceService = Depends(get_price_service),
):
    return await service.get_all(ticker)


@router.get("/last", response_model=PriceResponse)
async def get_last_price(
    ticker: str = Query(..., description="Currency ticker"),
    service: PriceService = Depends(get_price_service),
):
    price = await service.get_last(ticker)

    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    return price


@router.get("/by-date", response_model=list[PriceResponse])
async def get_prices_by_date(
    ticker: str = Query(...),
    date_from: int = Query(..., description="UNIX timestamp"),
    date_to: int = Query(..., description="UNIX timestamp"),
    service: PriceService = Depends(get_price_service),
):
    return await service.get_by_date(
        ticker=ticker,
        date_from=date_from,
        date_to=date_to,
    )
