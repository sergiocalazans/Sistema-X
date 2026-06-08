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
    from app import models  # noqa: F401

    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)
    # Mantém bancos já criados compatíveis com colunas adicionadas durante a evolução do projeto.
    migrate_professional_schema()
    migrate_patient_schema()


def migrate_professional_schema() -> None:
    inspector = inspect(engine)
    if "profissional" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("profissional")}
    dialect = engine.dialect.name

    with engine.begin() as connection:
        if "tipo_usuario" not in columns:
            connection.execute(text(_add_column_sql(dialect, "profissional", "tipo_usuario", "VARCHAR(40) NOT NULL DEFAULT 'profissional'")))


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
        if "nome_social" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "nome_social", "VARCHAR(120) NULL")))
        if "endereco" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "endereco", "VARCHAR(255) NULL")))
        if "origem_encaminhamento" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "origem_encaminhamento", "VARCHAR(160) NULL")))
        if "requisicao_medica" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "requisicao_medica", _text_sql(dialect, nullable=True))))
        if "status_jornada" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "status_jornada", "VARCHAR(80) NOT NULL DEFAULT 'cadastro'")))
        if "triagem_clinica" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "triagem_clinica", _text_sql(dialect, nullable=True))))
        if "triagem_socioeconomica" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "triagem_socioeconomica", _text_sql(dialect, nullable=True))))
        if "caracteristicas_fisicas" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "caracteristicas_fisicas", _text_sql(dialect, nullable=True))))
        if "foto_rosto" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "foto_rosto", "VARCHAR(255) NULL")))
        if "foto_perfil" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "foto_perfil", "VARCHAR(255) NULL")))
        if "foto_lado" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "foto_lado", "VARCHAR(255) NULL")))
        if "consentimento_lgpd" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "consentimento_lgpd", _boolean_sql(dialect, default=False))))
        if "observacoes_lgpd" not in columns:
            connection.execute(text(_add_column_sql(dialect, "paciente", "observacoes_lgpd", _text_sql(dialect, nullable=True))))
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

    migrate_assessment_schema()


def migrate_assessment_schema() -> None:
    inspector = inspect(engine)
    if "avaliacao" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("avaliacao")}
    dialect = engine.dialect.name

    with engine.begin() as connection:
        if "etapa_jornada" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "etapa_jornada", "VARCHAR(80) NOT NULL DEFAULT 'pre_avaliacao'")))
        if "requisicao_medica" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "requisicao_medica", _text_sql(dialect, nullable=True))))
        if "triagem_clinica" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "triagem_clinica", _text_sql(dialect, nullable=True))))
        if "triagem_socioeconomica" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "triagem_socioeconomica", _text_sql(dialect, nullable=True))))
        if "encaminhamento_exame" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "encaminhamento_exame", _text_sql(dialect, nullable=True))))
        if "resultado_exame" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "resultado_exame", "VARCHAR(40) NOT NULL DEFAULT 'aguardando'")))
        if "tipo_resultado" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "tipo_resultado", "VARCHAR(40) NULL")))
        if "plano_pos_diagnostico" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "plano_pos_diagnostico", _text_sql(dialect, nullable=True))))
        if "suporte_pos_diagnostico" not in columns:
            connection.execute(text(_add_column_sql(dialect, "avaliacao", "suporte_pos_diagnostico", _text_sql(dialect, nullable=True))))


def _add_column_sql(dialect: str, table: str, column: str, definition: str) -> str:
    if dialect == "sqlite":
        return f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
    return f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"


def _nullable_column_sql(dialect: str, table: str, column: str, definition: str) -> str:
    if dialect == "sqlite":
        return "SELECT 1"
    return f"ALTER TABLE `{table}` MODIFY COLUMN `{column}` {definition}"


def _text_sql(dialect: str, nullable: bool = True) -> str:
    null_sql = "NULL" if nullable else "NOT NULL"
    return f"TEXT {null_sql}"


def _boolean_sql(dialect: str, default: bool = False) -> str:
    value = "1" if default else "0"
    if dialect == "sqlite":
        return f"BOOLEAN NOT NULL DEFAULT {value}"
    return f"BOOLEAN NOT NULL DEFAULT {value}"

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
