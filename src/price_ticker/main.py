from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from admin.setup import setup_admin
from api.v1.price_tickers import router as price_tickers_router
from api.v1.system import router as system_router
from core.config import settings
from db import db_manager
from db.base import Base


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_admin(app)

    app.include_router(price_tickers_router, prefix="/api/v1")
    app.include_router(system_router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",  # Путь к приложению в формате "имя_файла:переменная_app"
        host="0.0.0.0",  # Принимать запросы со всех сетевых интерфейсов
        port=3005,  # Стандартный порт для разработки
        reload=True,  # Автоматическая перезагрузка сервера при изменении кода
    )
