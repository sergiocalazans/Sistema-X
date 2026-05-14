from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import Config


class Base(DeclarativeBase):
    pass


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _server_url(database_url: URL) -> URL:
    return URL.create(
        drivername=database_url.drivername,
        username=database_url.username,
        password=database_url.password,
        host=database_url.host,
        port=database_url.port,
        query=database_url.query,
    )


def create_database_if_not_exists() -> None:
    database_url = make_url(Config.SQLALCHEMY_DATABASE_URI)
    if not database_url.drivername.startswith("mysql") or not database_url.database:
        return

    server_engine = create_engine(_server_url(database_url), pool_pre_ping=True)
    database_name = database_url.database.replace("`", "``")
    charset = Config.MYSQL_CHARSET.replace("`", "")

    with server_engine.begin() as connection:
        connection.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
                f"CHARACTER SET {charset} COLLATE {charset}_unicode_ci"
            )
        )


def init_db() -> None:
    from app import models  # noqa: F401

    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
