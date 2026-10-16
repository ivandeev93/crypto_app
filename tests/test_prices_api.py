
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import get_price_service
from app.domain.entities.ticker import Ticker


@pytest.fixture
def service():
    mock = AsyncMock()
    app.dependency_overrides[get_price_service] = lambda: mock

    yield mock

    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


def make_price(ticker, price, timestamp):
    """Создаёт объект с полями, которые возвращает API."""
    return {
        "ticker": ticker,
        "price": price,
        "timestamp": timestamp,
    }


def test_root_returns_success_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "API is working"}


def test_get_all_prices(client, service):
    expected = [
        make_price("btc_usd", 65000.25, 1234567890),
        make_price("btc_usd", 65100.50, 1234567950),
    ]
    service.get_all.return_value = expected

    response = client.get("/prices/", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert response.json() == expected
    service.get_all.assert_awaited_once_with("btc_usd")


def test_get_all_prices_rejects_invalid_ticker(client, service):
    response = client.get("/prices/", params={"ticker": "invalid"})

    assert response.status_code == 422
    service.get_all.assert_not_awaited()


def test_get_last_price(client, service):
    expected = make_price("eth_usd", 3000.50, 1234567890)
    service.get_last.return_value = expected

    response = client.get("/prices/last", params={"ticker": "eth_usd"})

    assert response.status_code == 200
    assert response.json() == expected
    service.get_last.assert_awaited_once_with("eth_usd")


def test_get_last_price_returns_404_when_not_found(client, service):
    service.get_last.return_value = None

    response = client.get("/prices/last", params={"ticker": "btc_usd"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Price not found"


def test_get_prices_by_date(client, service):
    expected = [
        make_price("btc_usd", 65000.25, 1500),
    ]
    service.get_by_date.return_value = expected

    response = client.get(
        "/prices/by-date",
        params={
            "ticker": "btc_usd",
            "date_from": 1000,
            "date_to": 2000,
        },
    )

    assert response.status_code == 200
    assert response.json() == expected
    service.get_by_date.assert_awaited_once_with(
        ticker="btc_usd",
        date_from=1000,
        date_to=2000,
    )


def test_get_prices_by_date_requires_parameters(client, service):
    response = client.get("/prices/by-date", params={"ticker": "btc_usd"})

    assert response.status_code == 422
    service.get_by_date.assert_not_awaited()
