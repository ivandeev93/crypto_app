from unittest.mock import AsyncMock

import pytest

from app.domain.services.price import PriceService


@pytest.fixture
def repository():
    return AsyncMock()


@pytest.fixture
def service(repository):
    return PriceService(repository)


@pytest.mark.asyncio
async def test_save_price_delegates_to_repository(
    service, repository
):
    record = object()

    await service.save_price(record)

    repository.add.assert_awaited_once_with(record)


@pytest.mark.asyncio
async def test_get_all_delegates_to_repository(
    service, repository
):
    expected = [object(), object()]
    repository.get_all.return_value = expected

    result = await service.get_all("btc_usd")

    assert result == expected
    repository.get_all.assert_awaited_once_with("btc_usd")


@pytest.mark.asyncio
async def test_get_last_delegates_to_repository(
    service, repository
):
    expected = object()
    repository.get_last.return_value = expected

    result = await service.get_last("btc_usd")

    assert result is expected
    repository.get_last.assert_awaited_once_with("btc_usd")


@pytest.mark.asyncio
async def test_get_by_date_delegates_to_repository(
    service, repository
):
    expected = [object()]
    repository.get_by_date.return_value = expected

    result = await service.get_by_date(
        "btc_usd",
        date_from=1000,
        date_to=2000,
    )

    assert result == expected
    repository.get_by_date.assert_awaited_once_with(
        "btc_usd", 1000, 2000
    )
