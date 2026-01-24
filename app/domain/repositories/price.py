from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.price import PriceRecord

class PriceRepository(ABC):

    @abstractmethod
    async def add(self, record: PriceRecord) -> None:
        ...

    @abstractmethod
    async def get_all(self, ticker: str) -> List[PriceRecord]:
        ...

    @abstractmethod
    async def get_last(self, ticker: str) -> Optional[PriceRecord]:
        ...

    @abstractmethod
    async def get_by_date(
        self,
        ticker: str,
        date_from: int,
        date_to: int,
    ) -> List[PriceRecord]:
        ...
