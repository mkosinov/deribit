from fastapi import FastAPI

from admin.setup import setup_admin
from api.v1.price_tickers import router as price_tickers_router
from api.v1.system import router as system_router
from core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    setup_admin(app)

    app.include_router(price_tickers_router, prefix="/api/v1")
    app.include_router(system_router, prefix="/api/v1")

    return app


app = create_app()
