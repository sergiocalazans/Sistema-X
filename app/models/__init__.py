from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, func, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


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
        back_populates="profissional",
        cascade="all, delete-orphan",
    )
    avaliacoes: Mapped[list[Avaliacao]] = relationship(back_populates="profissional")


class Paciente(Base):
    __tablename__ = "paciente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[Sexo] = mapped_column(
        SQLEnum(Sexo, values_callable=enum_values, native_enum=True),
        nullable=False,
    )
    profissional_id: Mapped[int] = mapped_column(
        ForeignKey("profissional.id"),
        nullable=False,
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    profissional: Mapped[Profissional] = relationship(back_populates="pacientes")
    avaliacoes: Mapped[list[Avaliacao]] = relationship(
        back_populates="paciente",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def idade(self) -> int:
        hoje = date.today()
        return (
            hoje.year
            - self.data_nascimento.year
            - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        )

    @idade.expression
    def idade(cls):
        return func.timestampdiff(text("YEAR"), cls.data_nascimento, func.curdate())


class Sintoma(Base):
    __tablename__ = "sintoma"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    categoria: Mapped[str] = mapped_column(String(120), nullable=False)

    pesos: Mapped[list[PesoSintoma]] = relationship(
        back_populates="sintoma",
        cascade="all, delete-orphan",
    )
    avaliacoes_sintomas: Mapped[list[AvaliacaoSintoma]] = relationship(back_populates="sintoma")


class PesoSintoma(Base):
    __tablename__ = "peso_sintoma"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sintoma_id: Mapped[int] = mapped_column(ForeignKey("sintoma.id"), nullable=False)
    sexo_referencia: Mapped[Sexo] = mapped_column(
        SQLEnum(Sexo, values_callable=enum_values, native_enum=True),
        nullable=False,
    )
    peso: Mapped[float] = mapped_column(Float, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sintoma: Mapped[Sintoma] = relationship(back_populates="pesos")


class LimiarDecisao(Base):
    __tablename__ = "limiar_decisao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sexo: Mapped[Sexo] = mapped_column(
        SQLEnum(Sexo, values_callable=enum_values, native_enum=True),
        nullable=False,
    )
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

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
    realizado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    paciente: Mapped[Paciente] = relationship(back_populates="avaliacoes")
    profissional: Mapped[Profissional] = relationship(back_populates="avaliacoes")
    limiar_decisao: Mapped[LimiarDecisao] = relationship(back_populates="avaliacoes")
    sintomas: Mapped[list[AvaliacaoSintoma]] = relationship(
        back_populates="avaliacao",
        cascade="all, delete-orphan",
    )


class AvaliacaoSintoma(Base):
    __tablename__ = "avaliacao_sintoma"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    avaliacao_id: Mapped[int] = mapped_column(ForeignKey("avaliacao.id"), nullable=False)
    sintoma_id: Mapped[int] = mapped_column(ForeignKey("sintoma.id"), nullable=False)
    presente: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    avaliacao: Mapped[Avaliacao] = relationship(back_populates="sintomas")
    sintoma: Mapped[Sintoma] = relationship(back_populates="avaliacoes_sintomas")
