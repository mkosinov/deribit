from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "price_ticker"
    DATABASE_USER: str = "price_ticker"
    DATABASE_PASSWORD: str = "price_ticker"
    PROJECT_NAME: str = "Deribit client"
    LOG_LEVEL: str = "INFO"
    TRACKED_TICKERS: list[str] = ["btc_usd", "eth_usd"]
    REDIS_URL: str = "redis://localhost:6379/0"

    @property
    def database_connection_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD,
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            database=self.DATABASE_NAME,
        )


settings = Settings()
