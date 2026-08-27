from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the TrustLayer API."""

    environment: str = Field(default="development", alias="TRUSTLAYER_ENV")
    host: str = Field(default="0.0.0.0", alias="TRUSTLAYER_API_HOST")
    port: int = Field(default=8000, alias="TRUSTLAYER_API_PORT")
    database_url: str = Field(
        default="postgresql+asyncpg://trustlayer:trustlayer@localhost:5432/trustlayer",
        alias="TRUSTLAYER_API_DATABASE_URL",
    )
    jwt_secret: str = Field(alias="TRUSTLAYER_JWT_SECRET")
    jwt_issuer: str = Field(default="trustlayer", alias="TRUSTLAYER_JWT_ISSUER")
    access_token_minutes: int = Field(default=15, alias="TRUSTLAYER_ACCESS_TOKEN_MINUTES")
    refresh_token_days: int = Field(default=7, alias="TRUSTLAYER_REFRESH_TOKEN_DAYS")
    refresh_cookie_name: str = Field(
        default="trustlayer_refresh_token",
        alias="TRUSTLAYER_REFRESH_COOKIE_NAME",
    )
    cookie_secure: bool = Field(default=False, alias="TRUSTLAYER_COOKIE_SECURE")
    cookie_domain: str | None = Field(default=None, alias="TRUSTLAYER_COOKIE_DOMAIN")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        alias="TRUSTLAYER_CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
