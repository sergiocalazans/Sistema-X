from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, Text, func, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

paciente_profissional = Table(
    "paciente_profissional",
    Base.metadata,
    Column("paciente_id", ForeignKey("paciente.id"), primary_key=True),
    Column("profissional_id", ForeignKey("profissional.id"), primary_key=True),
    Column("criado_em", DateTime, server_default=func.now(), nullable=False),
)


class Sexo(str, Enum):
    MASCULINO = "masculino"
    FEMININO = "feminino"


def enum_values(enum_class: type[Enum]) -> list[str]:
    return [item.value for item in enum_class]


class Profissional(Base):
    __tablename__ = "profissional"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    especialidade: Mapped[str] = mapped_column(String(120), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    pacientes: Mapped[list[Paciente]] = relationship(
        secondary=paciente_profissional,
        back_populates="profissionais",
    )
    avaliacoes: Mapped[list[Avaliacao]] = relationship(back_populates="profissional")


class Paciente(Base):
    __tablename__ = "paciente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[Sexo] = mapped_column(SQLEnum(Sexo, values_callable=enum_values, native_enum=True), nullable=False)
    nome_social: Mapped[str | None] = mapped_column(String(120), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origem_encaminhamento: Mapped[str | None] = mapped_column(String(160), nullable=True)
    requisicao_medica: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_jornada: Mapped[str] = mapped_column(String(80), nullable=False, default="cadastro")
    triagem_clinica: Mapped[str | None] = mapped_column(Text, nullable=True)
    triagem_socioeconomica: Mapped[str | None] = mapped_column(Text, nullable=True)
    caracteristicas_fisicas: Mapped[str | None] = mapped_column(Text, nullable=True)
    foto_rosto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    foto_perfil: Mapped[str | None] = mapped_column(String(255), nullable=True)
    foto_lado: Mapped[str | None] = mapped_column(String(255), nullable=True)
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consentimento_email: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    observacoes_lgpd: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    profissionais: Mapped[list[Profissional]] = relationship(
        secondary=paciente_profissional,
        back_populates="pacientes",
    )
    avaliacoes: Mapped[list[Avaliacao]] = relationship(back_populates="paciente", cascade="all, delete-orphan")
    familiares: Mapped[list[FamiliarPaciente]] = relationship(back_populates="paciente", cascade="all, delete-orphan")
    documentos: Mapped[list[DocumentoPaciente]] = relationship(back_populates="paciente", cascade="all, delete-orphan")

    @hybrid_property
    def idade(self) -> int:
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )

    @idade.expression
    def idade(cls):
        return func.timestampdiff(text("YEAR"), cls.data_nascimento, func.curdate())


class Sintoma(Base):
    __tablename__ = "sintoma"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    categoria: Mapped[str] = mapped_column(String(120), nullable=False)

    pesos: Mapped[list[PesoSintoma]] = relationship(back_populates="sintoma", cascade="all, delete-orphan")
    avaliacoes_sintomas: Mapped[list[AvaliacaoSintoma]] = relationship(back_populates="sintoma")


class PesoSintoma(Base):
    __tablename__ = "peso_sintoma"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sintoma_id: Mapped[int] = mapped_column(ForeignKey("sintoma.id"), nullable=False)
    sexo_referencia: Mapped[Sexo] = mapped_column(SQLEnum(Sexo, values_callable=enum_values, native_enum=True), nullable=False)
    peso: Mapped[float] = mapped_column(Float, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    sintoma: Mapped[Sintoma] = relationship(back_populates="pesos")


class LimiarDecisao(Base):
    __tablename__ = "limiar_decisao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sexo: Mapped[Sexo] = mapped_column(SQLEnum(Sexo, values_callable=enum_values, native_enum=True), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    avaliacoes: Mapped[list[Avaliacao]] = relationship(back_populates="limiar_decisao")


class Avaliacao(Base):
    __tablename__ = "avaliacao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("paciente.id"), nullable=False)
    profissional_id: Mapped[int] = mapped_column(ForeignKey("profissional.id"), nullable=False)
    limiar_decisao_id: Mapped[int] = mapped_column(ForeignKey("limiar_decisao.id"), nullable=False)
    score_calculado: Mapped[float] = mapped_column(Float, nullable=False)
    encaminhar: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    observacao: Mapped[str | None] = mapped_column(String(500))
    etapa_jornada: Mapped[str] = mapped_column(String(80), nullable=False, default="pre_avaliacao")
    requisicao_medica: Mapped[str | None] = mapped_column(Text, nullable=True)
    triagem_clinica: Mapped[str | None] = mapped_column(Text, nullable=True)
    triagem_socioeconomica: Mapped[str | None] = mapped_column(Text, nullable=True)
    encaminhamento_exame: Mapped[str | None] = mapped_column(Text, nullable=True)
    resultado_exame: Mapped[str] = mapped_column(String(40), nullable=False, default="aguardando")
    tipo_resultado: Mapped[str | None] = mapped_column(String(40), nullable=True)
    plano_pos_diagnostico: Mapped[str | None] = mapped_column(Text, nullable=True)
    suporte_pos_diagnostico: Mapped[str | None] = mapped_column(Text, nullable=True)
    realizado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    paciente: Mapped[Paciente] = relationship(back_populates="avaliacoes")
    profissional: Mapped[Profissional] = relationship(back_populates="avaliacoes")
    limiar_decisao: Mapped[LimiarDecisao] = relationship(back_populates="avaliacoes")
    sintomas: Mapped[list[AvaliacaoSintoma]] = relationship(back_populates="avaliacao", cascade="all, delete-orphan")


class AvaliacaoSintoma(Base):
    __tablename__ = "avaliacao_sintoma"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    avaliacao_id: Mapped[int] = mapped_column(ForeignKey("avaliacao.id"), nullable=False)
    sintoma_id: Mapped[int] = mapped_column(ForeignKey("sintoma.id"), nullable=False)
    presente: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    avaliacao: Mapped[Avaliacao] = relationship(back_populates="sintomas")
    sintoma: Mapped[Sintoma] = relationship(back_populates="avaliacoes_sintomas")


class FamiliarPaciente(Base):
    __tablename__ = "familiar_paciente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("paciente.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    parentesco: Mapped[str | None] = mapped_column(String(80), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    momento_cadastro: Mapped[str] = mapped_column(String(30), nullable=False, default="pre_avaliacao")
    observacao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    paciente: Mapped[Paciente] = relationship(back_populates="familiares")


class DocumentoPaciente(Base):
    __tablename__ = "documento_paciente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("paciente.id"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(160), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(80), nullable=False, default="avaliacao_anterior")
    origem: Mapped[str | None] = mapped_column(String(160), nullable=True)
    nome_arquivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    caminho_arquivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    paciente: Mapped[Paciente] = relationship(back_populates="documentos")
