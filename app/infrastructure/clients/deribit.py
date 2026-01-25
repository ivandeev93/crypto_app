import aiohttp

class DeribitClient:
    BASE_URL = "https://www.deribit.com/api/v2/public"

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()

    async def get_index_price(self, ticker: str) -> float:
        """
        ticker: btc_usd | eth_usd
        """
        assert self._session is not None, "Session is not initialized"
        async with self._session.get(
            f"{self.BASE_URL}/get_index_price",
            params={"index_name": ticker},
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data["result"]["index_price"]
