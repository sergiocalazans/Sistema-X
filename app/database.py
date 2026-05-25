from sqlalchemy import create_engine, inspect, text
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
    import app 

    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)
    migrate_patient_schema()


def migrate_patient_schema() -> None:
    inspector = inspect(engine)
    if "paciente" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("paciente")}
    dialect = engine.dialect.name

    with engine.begin() as connection:
        if "cpf" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "cpf", "VARCHAR(14) NULL")))
        if "email" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "email", "VARCHAR(120) NULL")))
        if "telefone" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "telefone", "VARCHAR(20) NULL")))
        if "profissional_id" in columns:
            connection.execute(text(_nullable_column_sql(dialect, "paciente", "profissional_id", "INT NULL")))

        if "profissional_id" in columns and "paciente_profissional" in inspector.get_table_names():
            if dialect == "sqlite":
                connection.execute(text("""
                    INSERT OR IGNORE INTO paciente_profissional (paciente_id, profissional_id)
                    SELECT id, profissional_id
                    FROM paciente
                    WHERE profissional_id IS NOT NULL
                """))
            else:
                connection.execute(text("""
                    INSERT IGNORE INTO paciente_profissional (paciente_id, profissional_id)
                    SELECT id, profissional_id
                    FROM paciente
                    WHERE profissional_id IS NOT NULL
                """))


def _add_column_sql(dialect: str, table: str, column: str, definition: str) -> str:
    if dialect == "sqlite":
        return f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
    return f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"


def _nullable_column_sql(dialect: str, table: str, column: str, definition: str) -> str:
    if dialect == "sqlite":
        return "SELECT 1"
    return f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` {definition}"

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
