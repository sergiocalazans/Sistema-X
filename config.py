import os
from urllib.parse import quote_plus

try:
    from dbsenha import dbsenha
except ModuleNotFoundError:
    dbsenha = os.getenv("MYSQL_PASSWORD", "root")


def mysql_database_uri() -> str:
    user = os.getenv("MYSQL_USER", "root")
    password = quote_plus(dbsenha)
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "sistema-x")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        mysql_database_uri(),
    )
    MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")
