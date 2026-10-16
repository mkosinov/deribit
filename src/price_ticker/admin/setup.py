"""SQLAdmin model views and setup."""

from typing import ClassVar

from sqladmin import Admin, ModelView
from sqlalchemy import Column, create_engine

from db import db_manager
from db.base import Base
from models.price_ticker import PriceTickerRow


class PriceTickerAdmin(ModelView, model=PriceTickerRow):
    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True
    can_view_details: ClassVar[bool] = True
    form_include_pk: ClassVar[bool] = True
    column_list: ClassVar[list[Column]] = [
        PriceTickerRow.ticker,
        PriceTickerRow.price,
        PriceTickerRow.timestamp,
    ]
    column_searchable_list: ClassVar[list[Column]] = [PriceTickerRow.ticker]
    column_sortable_list: ClassVar[list[Column]] = [
        PriceTickerRow.ticker,
        PriceTickerRow.timestamp,
    ]
    form_columns: ClassVar[list[str]] = ["ticker", "price", "timestamp"]

    name = "PriceTicker"
    name_plural = "PriceTickers"
    icon = "fa-solid fa-box"


ALL_ADMIN_VIEWS: ClassVar = [PriceTickerAdmin]


def setup_admin(app) -> Admin:
    sync_url = str(db_manager.engine.url).replace(
        "sqlite+aiosqlite://", "sqlite://"
    )
    sync_engine = create_engine(sync_url)
    Base.metadata.create_all(sync_engine)
    admin = Admin(app, engine=sync_engine)
    for view_cls in ALL_ADMIN_VIEWS:
        admin.add_view(view_cls)
    return admin
