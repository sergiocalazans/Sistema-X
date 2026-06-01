import os
from urllib.parse import quote_plus


def load_env_file(path: str = ".env") -> None:
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


load_env_file()


def mysql_database_uri() -> str:
    user = os.getenv("MYSQL_USER", "root")
    password = quote_plus(os.getenv("MYSQL_PASSWORD", "root"))
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "sistema-x")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "sistema-x-dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        mysql_database_uri(),
    )
    MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "app", "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "sistema-x@localhost")
