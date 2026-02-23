from sqlalchemy import create_engine, text


def test_db_connection_query_executes():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()

    assert result == 1
