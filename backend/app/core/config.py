from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "boomtown"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    postgres_user: str = "boomtown"
    postgres_password: str = "boomtown"
    postgres_db: str = "boomtown"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    odds_api_base_url: str = "https://api.the-odds-api.com/v4"
    odds_api_key: str = ""
    odds_source_name: str = "the_odds_api"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
