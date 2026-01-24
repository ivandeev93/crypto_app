from fastapi import FastAPI
from app.api.routers import prices

app = FastAPI(title="Crypto Prices API")

app.include_router(prices.router)
