from sqlalchemy import Integer, String, Float, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base


class PriceModel(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("ticker", "timestamp", name="uq_ticker_timestamp"),
        Index("ix_prices_ticker", "ticker"),
        Index("ix_prices_timestamp", "timestamp"),
    )
