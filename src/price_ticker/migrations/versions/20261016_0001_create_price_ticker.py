from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "price_ticker",
        sa.Column("ticker", sa.String(length=48), nullable=False),
        sa.Column("price", sa.Numeric(precision=24, scale=12), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("ticker", "timestamp", name="pk_ticker_timestamp"),
        sa.CheckConstraint("ticker = LOWER(ticker)", name="ck_ticker_lowercase"),
        sa.CheckConstraint("ticker NOT LIKE '% %'", name="ck_ticker_no_spaces"),
    )


def downgrade() -> None:
    op.drop_table("price_ticker")
