from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import PrimaryKeyConstraint

from db.base import Base


class PriceTickerRow(Base):
    __tablename__ = "price_ticker"
    __table_args__ = (
        PrimaryKeyConstraint(
            "ticker", "timestamp", name="pk_ticker_timestamp"
        ),
        CheckConstraint("ticker = UPPER(ticker)", name="ck_ticker_uppercase"),
        CheckConstraint("ticker NOT LIKE '% %'", name="ck_ticker_no_spaces"),
    )

    ticker: Mapped[str] = mapped_column(String(48), nullable=False)
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=24, scale=12), nullable=False
    )
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
