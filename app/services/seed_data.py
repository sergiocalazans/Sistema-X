from __future__ import annotations

from datetime import date

from werkzeug.security import generate_password_hash

from app.database import SessionLocal
from app.models import LimiarDecisao, Paciente, PesoSintoma, Profissional, Sexo, Sintoma


SINTOMAS_MVP = [
    ("Deficiencia intelectual", "Cognitivo", 0.14, 0.13),
    ("Atraso na fala", "Comunicação", 0.09, 0.08),
    ("Dificuldades de aprendizagem", "Cognitivo", 0.08, 0.09),
    ("Déficit de atenção", "Comportamental", 0.07, 0.07),
    ("Hiperatividade", "Comportamental", 0.07, 0.06),
    ("Movimentos repetitivos", "Comportamental", 0.06, 0.06),
    ("Evitação de contato visual", "Comportamental", 0.06, 0.06),
    ("Dificuldade de interacao social", "Comportamental", 0.06, 0.07),
    ("Face alongada", "Físico", 0.07, 0.06),
    ("Orelhas proeminentes", "Físico", 0.06, 0.05),
    ("Macroorquidismo", "Físico", 0.09, 0.00),
]

SINTOMA_ALIASES = {
    "Comunicação": ["Comunicacao"],
    "Déficit de atenção": ["Deficit de atencao"],
    "Evitação de contato visual": ["Evitacao de contato visual"],
}

PACIENTES_DEMO = [
    ("Ana Silva Santos", Sexo.FEMININO, date(2018, 5, 1)),
    ("Pedro Oliveira Costa", Sexo.MASCULINO, date(2014, 4, 30)),
    ("Maria Souza Lima", Sexo.FEMININO, date(2020, 4, 29)),
]


def sync_profissional_demo(db):
    profissional = db.query(Profissional).filter_by(email="contato@sxf.com").first()
    if profissional:
        profissional.nome = "Dr. Admin"
        profissional.senha_hash = generate_password_hash("123456")
        profissional.especialidade = "Genética Médica"
        return profissional, False

    profissional = Profissional(
        nome="Dr. Admin",
        email="contato@sxf.com",
        senha_hash=generate_password_hash("123456"),
        especialidade="Genética Médica",
    )
    db.add(profissional)
    db.flush()
    return profissional, True


def sync_limiares(db):
    for sexo, valor in ((Sexo.MASCULINO, 0.56), (Sexo.FEMININO, 0.55)):
        limiar = db.query(LimiarDecisao).filter_by(sexo=sexo).first()
        if limiar:
            limiar.valor = valor
        else:
            db.add(LimiarDecisao(sexo=sexo, valor=valor))


def sync_sintomas(db):
    for descricao, categoria, peso_m, peso_f in SINTOMAS_MVP:
        descricoes_possiveis = [descricao, *SINTOMA_ALIASES.get(descricao, [])]
        sintoma = db.query(Sintoma).filter(Sintoma.descricao.in_(descricoes_possiveis)).first()
        if not sintoma:
            sintoma = Sintoma(descricao=descricao, categoria=categoria)
            db.add(sintoma)
            db.flush()
        else:
            sintoma.descricao = descricao
            sintoma.categoria = categoria

        for sexo, valor in ((Sexo.MASCULINO, peso_m), (Sexo.FEMININO, peso_f)):
            peso = db.query(PesoSintoma).filter_by(
                sintoma_id=sintoma.id,
                sexo_referencia=sexo,
            ).first()
            if peso:
                peso.peso = valor
            else:
                db.add(PesoSintoma(sintoma_id=sintoma.id, sexo_referencia=sexo, peso=valor))


def sync_pacientes_demo(db, profissional):
    for nome, sexo, nascimento in PACIENTES_DEMO:
        paciente = db.query(Paciente).filter_by(
            nome=nome,
            profissional_id=profissional.id,
        ).first()
        if paciente:
            paciente.data_nascimento = nascimento
            paciente.sexo = sexo
        else:
            db.add(Paciente(
                nome=nome,
                data_nascimento=nascimento,
                sexo=sexo,
                profissional_id=profissional.id,
            ))


def sync_mvp_defaults(include_demo_patients=False):
    db = SessionLocal()
    try:
        profissional, created = sync_profissional_demo(db)
        sync_limiares(db)
        sync_sintomas(db)
        if include_demo_patients:
            sync_pacientes_demo(db, profissional)

        db.commit()
        return {"profissional_created": created}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
