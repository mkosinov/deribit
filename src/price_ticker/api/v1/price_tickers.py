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


@router.get(
    "/all",
    response_model=PriceTickersPaginatedResponse,
    summary="List prices by ticker",
)
async def list_prices(
    ticker: Annotated[
        str,
        Query(
            min_length=3,
            max_length=48,
            pattern=r"^[A-Z0-9_-]+$",
            openapi_examples={"BTC_USD": {"value": "BTC_USD"}},
        ),
    ],
    pagination_query: Annotated[PaginationQuery, Depends()],
    service: Annotated[PriceTickerService, Depends(get_price_ticker_service)],
    db_session: SessionDep,
) -> PriceTickersPaginatedResponse:
    return await service.prices_by_ticker(
        db_session=db_session,
        ticker=ticker.upper(),
        pagination=pagination_query.to_domain(),
    )


@router.get(
    "/latest",
    response_model=PriceTickerResponse,
    summary="Get the latest price by ticker",
)
async def get_latest_price(
    ticker: Annotated[
        str,
        Query(
            min_length=3,
            max_length=48,
            pattern=r"^[A-Z0-9_-]+$",
            openapi_examples={"BTC_USD": {"value": "BTC_USD"}},
        ),
    ],
    service: Annotated[PriceTickerService, Depends(get_price_ticker_service)],
    db_session: SessionDep,
) -> PriceTickerResponse:
    result = await service.get_last_price(
        db_session=db_session, ticker=ticker.upper()
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prices for the ticker {ticker.upper()} found",
        )
    return result


@router.get(
    "/by_date",
    response_model=PriceTickersPaginatedResponse,
    summary="List prices by ticker for the specified period",
)
async def list_prices_by_period(
    ticker: Annotated[
        str,
        Query(
            min_length=3,
            max_length=48,
            pattern=r"^[A-Z0-9_-]+$",
            openapi_examples={"BTC_USD": {"value": "BTC_USD"}},
        ),
    ],
    pagination_query: Annotated[PaginationQuery, Depends()],
    period_query: Annotated[PeriodQuery, Depends()],
    service: Annotated[PriceTickerService, Depends(get_price_ticker_service)],
    db_session: SessionDep,
) -> PriceTickersPaginatedResponse:
    return await service.prices_by_ticker(
        db_session=db_session,
        ticker=ticker.upper(),
        pagination=pagination_query.to_domain(),
        period=period_query.to_domain(),
    )
