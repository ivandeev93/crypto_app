from dataclasses import dataclass

@dataclass(frozen=True)
class PriceRecord:
    ticker: str
    price: float
    timestamp: int
