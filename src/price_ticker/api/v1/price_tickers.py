from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from db import SessionDep
from schemas.pagination import PaginationQuery
from schemas.period import PeriodQuery
from schemas.price_ticker import (
    PriceTickerResponse,
    PriceTickersPaginatedResponse,
)
from services.price_ticker import (
    PriceTickerService,
    get_price_ticker_service,
)

router = APIRouter(tags=["Deribit prices"])

TickerParam = Annotated[
    str,
    Query(
        min_length=3,
        max_length=48,
        pattern=r"^[a-zA-Z0-9_-]+$",
        openapi_examples={
            "btc_usd": {"value": "btc_usd"},
            "eth_usd": {"value": "eth_usd"},
        },
    ),
]
StartDateParam = Annotated[
    date | None,
    Query(
        description="Начальная дата периода, формат YYYY-MM-DD",
        openapi_examples={
            "2026-10-15": {"value": "2026-10-15"},
            "2026-10-16": {"value": "2026-10-16"},
        },
    ),
]
EndDateParam = Annotated[
    date | None,
    Query(
        description="Конечная дата периода включительно, формат YYYY-MM-DD",
        openapi_examples={
            "2026-10-16": {"value": "2026-10-16"},
            "2026-10-15": {"value": "2026-10-15"},
        },
    ),
]


@router.get(
    "/prices/all",
    response_model=list[PriceTickerResponse],
    summary="All prices by ticker",
)
async def list_prices(
    ticker: TickerParam,
    service: Annotated[PriceTickerService, Depends(get_price_ticker_service)],
    db_session: SessionDep,
) -> list[PriceTickerResponse]:
    return await service.list_prices(
        db_session=db_session, ticker=ticker.lower()
    )


@router.get(
    "/prices/latest",
    response_model=PriceTickerResponse,
    summary="Get the latest price by ticker",
)
async def get_latest_price(
    ticker: TickerParam,
    service: Annotated[PriceTickerService, Depends(get_price_ticker_service)],
    db_session: SessionDep,
) -> PriceTickerResponse:
    result = await service.get_last_price(
        db_session=db_session, ticker=ticker.lower()
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prices for the ticker {ticker.lower()} found",
        )
    return result


@router.get(
    "/prices/period",
    response_model=PriceTickersPaginatedResponse,
    summary="List prices by ticker for the specified period",
)
async def list_prices_by_period(
    ticker: TickerParam,
    pagination_query: Annotated[PaginationQuery, Depends()],
    service: Annotated[PriceTickerService, Depends(get_price_ticker_service)],
    db_session: SessionDep,
    start_date: StartDateParam = None,
    end_date: EndDateParam = None,
) -> PriceTickersPaginatedResponse:
    period_query = PeriodQuery(start_date=start_date, end_date=end_date)
    return await service.list_prices_page(
        db_session=db_session,
        ticker=ticker.lower(),
        pagination=pagination_query.to_domain(),
        period=period_query.to_domain(),
    )
