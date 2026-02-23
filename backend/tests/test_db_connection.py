from sqlalchemy import create_engine, text

from app.core.config import Settings


def test_db_connection_query_executes_with_sqlite_probe():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()

    assert result == 1


def test_settings_builds_postgres_dsn():
    settings = Settings(
        postgres_user="boomtown",
        postgres_password="boomtown",
        postgres_db="boomtown",
        postgres_host="postgres",
        postgres_port=5432,
    )

    assert settings.database_url == "postgresql+psycopg://boomtown:boomtown@postgres:5432/boomtown"
