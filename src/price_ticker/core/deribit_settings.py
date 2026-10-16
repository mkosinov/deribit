from pydantic_settings import BaseSettings, SettingsConfigDict


class DeribitSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DERIBIT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    API_URL: str = "https://www.deribit.com"
    API_PREFIX: str = "/api/v2/public"
    TIMEOUT_SECONDS: float = 10.0


deribit_settings = DeribitSettings()
