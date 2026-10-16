
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.domain.entities.price import PriceRecord
from app.domain.entities.ticker import Ticker
from app.infrastructure.repositories.price import PriceRepositoryImpl


@pytest.fixture
def session():
    """Имитация асинхронной сессии SQLAlchemy."""
    mock = MagicMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.execute = AsyncMock()
    return mock


@pytest.fixture
def repository(session):
    return PriceRepositoryImpl(session)


def make_model(ticker, price, timestamp):
    """Имитация ORM-модели, возвращаемой запросом."""
    return SimpleNamespace(
        ticker=ticker,
        price=price,
        timestamp=timestamp,
    )


@pytest.mark.asyncio
async def test_add_saves_price(repository, session):
    record = PriceRecord(
        ticker=Ticker.btc_usd,
        price=65000.25,
        timestamp=1234567890,
    )

    session.add = MagicMock()

    await repository.add(record)

    session.add.assert_called_once()
    saved_model = session.add.call_args.args[0]

    assert saved_model.ticker == record.ticker
    assert saved_model.price == record.price
    assert saved_model.timestamp == record.timestamp
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_rolls_back_on_integrity_error(repository, session):
    session.commit.side_effect = IntegrityError(
        "INSERT INTO prices",
        {},
        Exception("duplicate"),
    )

    record = PriceRecord(
        ticker=Ticker.btc_usd,
        price=65000.25,
        timestamp=1234567890,
    )

    with pytest.raises(IntegrityError):
        await repository.add(record)

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_returns_prices(repository, session):
    rows = [
        make_model(Ticker.btc_usd, 65000.25, 1000),
        make_model(Ticker.btc_usd, 65100.50, 2000),
    ]

    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    session.execute.return_value = result

    prices = await repository.get_all("btc_usd")

    assert len(prices) == 2
    assert prices[0].ticker == Ticker.btc_usd
    assert prices[0].price == 65000.25
    assert prices[0].timestamp == 1000
    assert prices[1].price == 65100.50

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_returns_empty_list(repository, session):
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result

    prices = await repository.get_all("btc_usd")

    assert prices == []


@pytest.mark.asyncio
async def test_get_last_returns_latest_price(repository, session):
    row = make_model(Ticker.btc_usd, 65100.50, 2000)

    result = MagicMock()
    result.scalar_one_or_none.return_value = row
    session.execute.return_value = result

    price = await repository.get_last("btc_usd")

    assert price is not None
    assert price.ticker == Ticker.btc_usd
    assert price.price == 65100.50
    assert price.timestamp == 2000

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_last_returns_none_when_not_found(repository, session):
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    price = await repository.get_last("btc_usd")

    assert price is None


@pytest.mark.asyncio
async def test_get_by_date_returns_prices_in_period(repository, session):
    rows = [
        make_model(Ticker.btc_usd, 65000.25, 1500),
        make_model(Ticker.btc_usd, 65100.50, 2000),
    ]

    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    session.execute.return_value = result

    prices = await repository.get_by_date(
        ticker="btc_usd",
        date_from=1000,
        date_to=2000,
    )

    assert len(prices) == 2
    assert [price.timestamp for price in prices] == [1500, 2000]
    session.execute.assert_awaited_once()
