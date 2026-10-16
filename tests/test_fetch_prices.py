
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.entities.ticker import Ticker
from app.services.tasks import fetch_prices as fetch_prices_module


@pytest.fixture
def dependencies(monkeypatch):
    """Подменяет внешние зависимости задачи моками."""

    # Имитация клиента Deribit
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.get_index_price = AsyncMock()

    monkeypatch.setattr(
        fetch_prices_module,
        "DeribitClient",
        lambda: client,
    )

    # Имитация асинхронной сессии PostgreSQL
    session = AsyncMock()
    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=session)
    session_context.__aexit__ = AsyncMock(return_value=False)

    monkeypatch.setattr(
        fetch_prices_module,
        "AsyncSessionLocal",
        lambda: session_context,
    )

    # Имитация репозитория
    repository = MagicMock()
    monkeypatch.setattr(
        fetch_prices_module,
        "PriceRepositoryImpl",
        lambda session: repository,
    )

    # Имитация бизнес-сервиса
    service = MagicMock()
    service.save_price = AsyncMock()

    monkeypatch.setattr(
        fetch_prices_module,
        "PriceService",
        lambda repository: service,
    )

    return {
        "client": client,
        "session": session,
        "service": service,
    }


@pytest.mark.asyncio
async def test_fetch_prices_saves_price(dependencies, monkeypatch):
    """Успешное получение и сохранение цены."""

    client = dependencies["client"]
    service = dependencies["service"]

    client.get_index_price.return_value = 65000.25
    monkeypatch.setattr(fetch_prices_module.time, "time", lambda: 1234567890)

    await fetch_prices_module.fetch_prices_async(
        tickers=(Ticker.btc_usd,)
    )

    client.get_index_price.assert_awaited_once_with("btc_usd")
    service.save_price.assert_awaited_once()

    record = service.save_price.await_args.args[0]

    assert record.ticker == Ticker.btc_usd
    assert record.price == 65000.25
    assert record.timestamp == 1234567890


@pytest.mark.asyncio
async def test_fetch_prices_continues_after_fetch_error(dependencies):
    """Ошибка одного тикера не мешает обработать следующий."""

    client = dependencies["client"]
    service = dependencies["service"]

    client.get_index_price.side_effect = [
        RuntimeError("Deribit unavailable"),
        3000.50,
    ]

    await fetch_prices_module.fetch_prices_async(
        tickers=(Ticker.btc_usd, Ticker.eth_usd)
    )

    assert client.get_index_price.await_count == 2
    service.save_price.assert_awaited_once()

    record = service.save_price.await_args.args[0]
    assert record.ticker == Ticker.eth_usd
    assert record.price == 3000.50


@pytest.mark.asyncio
async def test_fetch_prices_raises_when_no_prices_saved(dependencies):
    """Если ни одна цена не сохранена, возникает RuntimeError."""

    client = dependencies["client"]

    client.get_index_price.side_effect = RuntimeError(
        "Deribit unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="Не удалось получить и сохранить ни одной цены",
    ):
        await fetch_prices_module.fetch_prices_async(
            tickers=(Ticker.btc_usd,)
        )


@pytest.mark.asyncio
async def test_fetch_prices_rolls_back_on_save_error(dependencies):
    """При ошибке сохранения выполняется откат транзакции."""

    client = dependencies["client"]
    session = dependencies["session"]
    service = dependencies["service"]

    client.get_index_price.return_value = 65000.25
    service.save_price.side_effect = ValueError("Database error")

    with pytest.raises(ValueError, match="Database error"):
        await fetch_prices_module.fetch_prices_async(
            tickers=(Ticker.btc_usd,)
        )

    session.rollback.assert_awaited_once()
