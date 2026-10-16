
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from app.infrastructure.clients.deribit import DeribitClient


def make_mock_session(payload):
    """Создаёт поддельную HTTP-сессию с заданным JSON-ответом."""
    session = MagicMock()
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json = AsyncMock(return_value=payload)

    request_context = MagicMock()
    request_context.__aenter__ = AsyncMock(return_value=response)
    request_context.__aexit__ = AsyncMock(return_value=False)

    session.get.return_value = request_context

    return session, response


@pytest.mark.asyncio
async def test_get_index_price_returns_price():
    client = DeribitClient()
    session, _ = make_mock_session(
        {"result": {"index_price": 65000.25}}
    )
    client._session = session

    price = await client.get_index_price("btc_usd")

    assert price == 65000.25
    session.get.assert_called_once()

    _, kwargs = session.get.call_args
    assert kwargs["params"] == {"index_name": "btc_usd"}


@pytest.mark.asyncio
async def test_get_index_price_converts_price_to_float():
    client = DeribitClient()
    session, _ = make_mock_session(
        {"result": {"index_price": "65000.25"}}
    )
    client._session = session

    price = await client.get_index_price("btc_usd")

    assert price == 65000.25
    assert isinstance(price, float)


@pytest.mark.asyncio
async def test_get_index_price_raises_http_error():
    client = DeribitClient()
    session, response = make_mock_session({})
    client._session = session

    response.raise_for_status.side_effect = aiohttp.ClientError(
        "HTTP error"
    )

    with pytest.raises(aiohttp.ClientError):
        await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_raises_api_error():
    client = DeribitClient()
    session, _ = make_mock_session(
        {"error": {"code": 10028, "message": "too_many_requests"}}
    )
    client._session = session

    with pytest.raises(RuntimeError, match="Deribit API error"):
        await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_rejects_unexpected_response():
    client = DeribitClient()
    session, _ = make_mock_session({"result": {}})
    client._session = session

    with pytest.raises(RuntimeError, match="Unexpected Deribit API response"):
        await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_requires_context_manager():
    client = DeribitClient()

    with pytest.raises(RuntimeError, match="async context manager"):
        await client.get_index_price("btc_usd")
