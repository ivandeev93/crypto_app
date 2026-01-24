import aiohttp

class DeribitClient:
    BASE_URL = "https://www.deribit.com/api/v2/public"

    async def get_index_price(self, ticker: str) -> float:
        """
        ticker: btc_usd | eth_usd
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/get_index_price",
                params={"index_name": ticker},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                data = await response.json()

                return data["result"]["index_price"]
