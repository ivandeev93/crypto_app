from sqlalchemy import Column, Integer, String, Float
from app.infrastructure.db.base import Base


class PriceModel(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False, index=True)
