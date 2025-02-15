from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env")

    POSTGRES_DB: str = "proctoring"
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    DB_HOST: str = "db"
    DP_PORT: str = "5432"

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.DB_HOST}:{self.DP_PORT}/{self.POSTGRES_DB}"
        )

    CRYPTO_KEY: bytes = b"some_key"

    TOKEN_SECRET_KEY: str = "some_secret"
    GENERATE_TOKEN_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
