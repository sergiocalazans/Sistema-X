from datetime import date, datetime

from flask import Blueprint, jsonify, render_template, request, send_file, session
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import SessionLocal
from app.models import (
    Avaliacao,
    AvaliacaoSintoma,
    LimiarDecisao,
    Paciente,
    PesoSintoma,
    Profissional,
    Sexo,
    Sintoma,
)
from app.services.reports import build_reports
from app.services.exports import assessments_workbook, patients_workbook

main_bp = Blueprint("main", __name__)


def current_professional_id():
    return session.get("profissional_id")


def require_auth():
    profissional_id = current_professional_id()
    if not profissional_id:
        return None, (jsonify({"error": "Autenticação obrigatória"}), 401)
    return profissional_id, None


def parse_birth_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def normalize_optional(value):
    return (value or "").strip() or None


def current_professional_patient_query(db, profissional_id):
    return (
        db.query(Paciente)
        .join(Paciente.profissionais)
        .filter(Profissional.id == profissional_id)
    )


def paciente_json(paciente):
    ultima = max(paciente.avaliacoes, key=lambda a: a.realizado_em, default=None)
    return {
        "id": paciente.id,
        "name": paciente.nome,
        "cpf": paciente.cpf or "",
        "email": paciente.email or "",
        "telefone": paciente.telefone or "",
        "sex": "F" if paciente.sexo == Sexo.FEMININO else "M",
        "sexo": paciente.sexo.value,
        "birthDate": paciente.data_nascimento.isoformat(),
        "date": paciente.criado_em.strftime("%d/%m/%Y"),
        "age": paciente.idade,
        "score": round(ultima.score_calculado, 2) if ultima else 0,
        "rec": "encaminhar" if ultima and ultima.encaminhar else "nao-prio",
    }


def avaliacao_json(avaliacao):
    paciente = avaliacao.paciente
    return {
        "id": avaliacao.id,
        "patientId": paciente.id,
        "patientName": paciente.nome,
        "sex": "F" if paciente.sexo == Sexo.FEMININO else "M",
        "score": round(avaliacao.score_calculado, 2),
        "threshold": round(avaliacao.limiar_decisao.valor, 2),
        "rec": "encaminhar" if avaliacao.encaminhar else "nao-prio",
        "recommendation": "Encaminhar" if avaliacao.encaminhar else "Não prioritário",
        "observacao": avaliacao.observacao,
        "date": avaliacao.realizado_em.strftime("%d/%m/%Y %H:%M"),
        "symptoms": [
            {
                "id": item.sintoma_id,
                "description": item.sintoma.descricao,
                "present": item.presente,
            }
            for item in avaliacao.sintomas
        ],
    }


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""
    nome = (data.get("nome") or "Profissional").strip()
    especialidade = (data.get("especialidade") or "Saúde").strip()

    if not email or not senha:
        return jsonify({"error": "Informe e-mail e senha"}), 400
    if len(senha) < 6:
        return jsonify({"error": "A senha deve ter pelo menos 6 caracteres"}), 400

    db = SessionLocal()
    try:
        if db.query(Profissional).filter(func.lower(Profissional.email) == email).first():
            return jsonify({"error": "E-mail ja cadastrado"}), 409

        profissional = Profissional(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            especialidade=especialidade,
        )
        db.add(profissional)
        db.commit()
        db.refresh(profissional)
        session["profissional_id"] = profissional.id
        return jsonify({"id": profissional.id, "email": profissional.email, "nome": profissional.nome}), 201
    finally:
        db.close()


@main_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""

    db = SessionLocal()
    try:
        profissional = db.query(Profissional).filter(func.lower(Profissional.email) == email).first()
        if not profissional or not check_password_hash(profissional.senha_hash, senha):
            return jsonify({"error": "E-mail ou senha inválidos"}), 401

        session["profissional_id"] = profissional.id
        return jsonify({"id": profissional.id, "email": profissional.email, "nome": profissional.nome})
    finally:
        db.close()


@main_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@main_bp.route("/api/auth/me")
def me():
    profissional_id = current_professional_id()
    if not profissional_id:
        return jsonify({"authenticated": False})

    db = SessionLocal()
    try:
        profissional = db.get(Profissional, profissional_id)
        if not profissional:
            session.clear()
            return jsonify({"authenticated": False})
        return jsonify({
            "authenticated": True,
            "id": profissional.id,
            "email": profissional.email,
            "nome": profissional.nome,
            "especialidade": profissional.especialidade,
        })
    finally:
        db.close()


@main_bp.route("/api/auth/profile", methods=["PUT"])
def update_profile():
    profissional_id, error = require_auth()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip().lower()
    especialidade = (data.get("especialidade") or "").strip()

    if not nome or not email or not especialidade:
        return jsonify({"error": "Informe nome, e-mail e especialidade"}), 400

    db = SessionLocal()
    try:
        existing = (
            db.query(Profissional)
            .filter(func.lower(Profissional.email) == email, Profissional.id != profissional_id)
            .first()
        )
        if existing:
            return jsonify({"error": "E-mail ja cadastrado por outro usuario"}), 409

        profissional = db.get(Profissional, profissional_id)
        if not profissional:
            session.clear()
            return jsonify({"error": "Usuario nao encontrado"}), 404

        profissional.nome = nome
        profissional.email = email
        profissional.especialidade = especialidade
        db.commit()
        db.refresh(profissional)

        return jsonify({
            "id": profissional.id,
            "email": profissional.email,
            "nome": profissional.nome,
            "especialidade": profissional.especialidade,
        })
    finally:
        db.close()


@main_bp.route("/api/auth/password", methods=["PUT"])
def update_password():
    profissional_id, error = require_auth()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    senha_atual = data.get("senha_atual") or ""
    nova_senha = data.get("nova_senha") or ""
    confirmar_senha = data.get("confirmar_senha") or ""

    if not senha_atual or not nova_senha or not confirmar_senha:
        return jsonify({"error": "Preencha todos os campos de senha"}), 400
    if len(nova_senha) < 6:
        return jsonify({"error": "A nova senha deve ter pelo menos 6 caracteres"}), 400
    if nova_senha != confirmar_senha:
        return jsonify({"error": "A confirmacao da senha nao confere"}), 400

    db = SessionLocal()
    try:
        profissional = db.get(Profissional, profissional_id)
        if not profissional:
            session.clear()
            return jsonify({"error": "Usuario nao encontrado"}), 404
        if not check_password_hash(profissional.senha_hash, senha_atual):
            return jsonify({"error": "Senha atual invalida"}), 401

        profissional.senha_hash = generate_password_hash(nova_senha)
        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()


@main_bp.route("/api/pacientes")
def get_pacientes():
    profissional_id, error = require_auth()
    if error:
        return error

    db = SessionLocal()
    try:
        pacientes = (
            current_professional_patient_query(db, profissional_id)
            .order_by(Paciente.criado_em.desc())
            .all()
        )
        return jsonify([paciente_json(p) for p in pacientes])
    finally:
        db.close()


@main_bp.route("/api/pacientes", methods=["POST"])
def create_paciente():
    profissional_id, error = require_auth()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    try:
        nome = (data.get("nome") or "").strip()
        sexo = Sexo(data.get("sexo"))
        data_nascimento = parse_birth_date(data.get("data_nascimento"))
    except (ValueError, TypeError):
        return jsonify({"error": "Dados do paciente inválidos"}), 400

    if not nome or not data_nascimento:
        return jsonify({"error": "Informe nome, data de nascimento e sexo"}), 400
    if data_nascimento > date.today():
        return jsonify({"error": "Data de nascimento não pode ser futura"}), 400

    db = SessionLocal()
    try:
        profissional = db.get(Profissional, profissional_id)
        cpf = normalize_optional(data.get("cpf"))
        paciente = db.query(Paciente).filter(Paciente.cpf == cpf).first() if cpf else None

        if paciente:
            paciente.nome = nome
            paciente.email = normalize_optional(data.get("email"))
            paciente.telefone = normalize_optional(data.get("telefone"))
            paciente.data_nascimento = data_nascimento
            paciente.sexo = sexo
        else:
            paciente = Paciente(
                nome=nome,
                cpf=cpf,
                email=normalize_optional(data.get("email")),
                telefone=normalize_optional(data.get("telefone")),
                data_nascimento=data_nascimento,
                sexo=sexo,
            )
            db.add(paciente)

        if profissional and profissional not in paciente.profissionais:
            paciente.profissionais.append(profissional)

        db.commit()
        db.refresh(paciente)
        return jsonify(paciente_json(paciente)), 201
    finally:
        db.close()


@main_bp.route("/api/pacientes/<int:paciente_id>", methods=["PUT"])
def update_paciente(paciente_id):
    profissional_id, error = require_auth()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    db = SessionLocal()
    try:
        paciente = (
            current_professional_patient_query(db, profissional_id)
            .filter(Paciente.id == paciente_id)
            .first()
        )
        if not paciente:
            return jsonify({"error": "Paciente não encontrado"}), 404

        if "nome" in data:
            paciente.nome = (data.get("nome") or "").strip()
        if "cpf" in data:
            cpf = normalize_optional(data.get("cpf"))
            existing = db.query(Paciente).filter(Paciente.cpf == cpf, Paciente.id != paciente.id).first() if cpf else None
            if existing:
                return jsonify({"error": "CPF ja cadastrado para outro paciente"}), 409
            paciente.cpf = cpf
        if "email" in data:
            paciente.email = normalize_optional(data.get("email"))
        if "telefone" in data:
            paciente.telefone = normalize_optional(data.get("telefone"))
        if "sexo" in data:
            paciente.sexo = Sexo(data.get("sexo"))
        if "data_nascimento" in data:
            paciente.data_nascimento = parse_birth_date(data.get("data_nascimento"))

        if not paciente.nome or not paciente.data_nascimento:
            return jsonify({"error": "Dados do paciente inválidos"}), 400
        if paciente.data_nascimento > date.today():
            return jsonify({"error": "Data de nascimento não pode ser futura"}), 400

        db.commit()
        db.refresh(paciente)
        return jsonify(paciente_json(paciente))
    except (ValueError, TypeError):
        db.rollback()
        return jsonify({"error": "Dados do paciente inválidos"}), 400
    finally:
        db.close()


@main_bp.route("/api/pacientes/export")
def export_pacientes():
    profissional_id, error = require_auth()
    if error:
        return error

    db = SessionLocal()
    try:
        workbook = patients_workbook(db, profissional_id)
        return send_file(
            workbook,
            as_attachment=True,
            download_name="pacientes.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    finally:
        db.close()


@main_bp.route("/api/sintomas")
def get_sintomas():
    _, error = require_auth()
    if error:
        return error

    db = SessionLocal()
    try:
        sintomas = db.query(Sintoma).order_by(Sintoma.categoria, Sintoma.descricao).all()
        return jsonify([
            {"id": s.id, "description": s.descricao, "category": s.categoria}
            for s in sintomas
        ])
    finally:
        db.close()


@main_bp.route("/api/avaliacoes")
def get_avaliacoes():
    profissional_id, error = require_auth()
    if error:
        return error

    db = SessionLocal()
    try:
        avaliacoes = (
            db.query(Avaliacao)
            .filter(Avaliacao.profissional_id == profissional_id)
            .order_by(Avaliacao.realizado_em.desc())
            .all()
        )
        return jsonify([avaliacao_json(a) for a in avaliacoes])
    finally:
        db.close()


@main_bp.route("/api/avaliacoes/export")
def export_avaliacoes():
    profissional_id, error = require_auth()
    if error:
        return error

    db = SessionLocal()
    try:
        workbook = assessments_workbook(db, profissional_id)
        return send_file(
            workbook,
            as_attachment=True,
            download_name="historico-avaliacoes.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    finally:
        db.close()


@main_bp.route("/api/avaliacoes", methods=["POST"])
def create_avaliacao():
    profissional_id, error = require_auth()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    paciente_id = data.get("paciente_id")
    try:
        sintomas_presentes = {int(sintoma_id) for sintoma_id in (data.get("sintomas") or [])}
    except (TypeError, ValueError):
        return jsonify({"error": "Lista de sintomas inválida"}), 400
    observacao = (data.get("observacao") or "").strip() or None

    db = SessionLocal()
    try:
        paciente = (
            current_professional_patient_query(db, profissional_id)
            .filter(Paciente.id == paciente_id)
            .first()
        )
        if not paciente:
            return jsonify({"error": "Paciente não encontrado"}), 404

        limiar = db.query(LimiarDecisao).filter(LimiarDecisao.sexo == paciente.sexo).first()
        if not limiar:
            return jsonify({"error": "Limiar de decisão não cadastrado para o sexo do paciente"}), 400

        sintomas = db.query(Sintoma).all()
        pesos = {
            peso.sintoma_id: peso.peso
            for peso in db.query(PesoSintoma).filter(PesoSintoma.sexo_referencia == paciente.sexo).all()
        }
        score = sum(pesos.get(sintoma.id, 0) for sintoma in sintomas if sintoma.id in sintomas_presentes)
        encaminhar = score >= limiar.valor

        avaliacao = Avaliacao(
            paciente_id=paciente.id,
            profissional_id=profissional_id,
            limiar_decisao_id=limiar.id,
            score_calculado=score,
            encaminhar=encaminhar,
            observacao=observacao,
        )
        db.add(avaliacao)
        db.flush()

        for sintoma in sintomas:
            db.add(AvaliacaoSintoma(
                avaliacao_id=avaliacao.id,
                sintoma_id=sintoma.id,
                presente=sintoma.id in sintomas_presentes,
            ))

        db.commit()
        db.refresh(avaliacao)
        return jsonify(avaliacao_json(avaliacao)), 201
    finally:
        db.close()


@main_bp.route("/api/relatorios")
def get_relatorios():
    profissional_id, error = require_auth()
    if error:
        return error

    db = SessionLocal()
    try:
        return jsonify(build_reports(db, profissional_id))
    finally:
        db.close()
