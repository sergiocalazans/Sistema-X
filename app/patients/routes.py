from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from app.models import DocumentoPaciente, FamiliarPaciente, Paciente, Profissional, Sexo
from app.services.exports import patients_workbook
from app.shared.auth import ROLE_ADMIN, ROLE_PROFESSIONAL, current_professional_id, current_user_role, role_required
from app.shared.db import db_session
from app.shared.formatters import patient_last_assessment, patient_last_score, recommendation_key, sex_label
from app.shared.patients import professional_patient_query

patients_bp = Blueprint("patients", __name__, url_prefix="/pacientes")


@patients_bp.get("")
@role_required(ROLE_ADMIN, ROLE_PROFESSIONAL)
def index():
    profissional_id = current_professional_id()
    with db_session() as db:
        pacientes = (
            professional_patient_query(db, profissional_id)
            .order_by(Paciente.criado_em.desc())
            .all()
        )
        rows = []
        for paciente in pacientes:
            ultima = patient_last_assessment(paciente)
            rows.append({
                "id": paciente.id,
                "name": paciente.nome,
                "professionals": _professionals_label(paciente),
                "cpf": paciente.cpf or "-",
                "email": paciente.email or "-",
                "phone": paciente.telefone or "-",
                "sex": sex_label(paciente.sexo),
                "age": paciente.idade,
                "score": patient_last_score(paciente),
                "recommendation_key": recommendation_key(ultima.encaminhar) if ultima else "nao-prio",
                "stage": _stage_label(paciente.status_jornada),
            })

        return render_template(
            "pages/patients.html",
            active_page="patients",
            patients=rows,
            show_professional_column=current_user_role() == ROLE_ADMIN,
        )


@patients_bp.route("/novo", methods=["GET", "POST"])
@role_required(ROLE_ADMIN, ROLE_PROFESSIONAL)
def create():
    if request.method == "POST":
        return save_patient()
    return render_template("pages/patient_form.html", active_page="patients", patient=None)


@patients_bp.route("/<int:patient_id>/editar", methods=["GET", "POST"])
@role_required(ROLE_ADMIN, ROLE_PROFESSIONAL)
def edit(patient_id):
    profissional_id = current_professional_id()
    with db_session() as db:
        paciente = professional_patient_query(db, profissional_id).filter(Paciente.id == patient_id).first()
        if not paciente:
            flash("Paciente não encontrado.", "error")
            return redirect(url_for("patients.index"))

        if request.method == "POST":
            return save_patient(paciente.id)

        return render_template("pages/patient_form.html", active_page="patients", patient=paciente)


@patients_bp.get("/export")
@role_required(ROLE_ADMIN, ROLE_PROFESSIONAL)
def export():
    profissional_id = current_professional_id()
    with db_session() as db:
        workbook = patients_workbook(db, profissional_id, include_all=current_user_role() == ROLE_ADMIN)
        return send_file(
            workbook,
            as_attachment=True,
            download_name="pacientes.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


@patients_bp.get("/<int:patient_id>/arquivo/<path:filename>")
@role_required(ROLE_ADMIN, ROLE_PROFESSIONAL)
def patient_file(patient_id, filename):
    profissional_id = current_professional_id()
    with db_session() as db:
        paciente = professional_patient_query(db, profissional_id).filter(Paciente.id == patient_id).first()
        if not paciente:
            flash("Paciente não encontrado.", "error")
            return redirect(url_for("patients.index"))

    directory = (Path(current_app.config["UPLOAD_FOLDER"]) / "pacientes" / str(patient_id)).resolve()
    requested = (directory / filename).resolve()
    if directory not in requested.parents and requested != directory:
        flash("Arquivo inválido.", "error")
        return redirect(url_for("patients.edit", patient_id=patient_id))
    if not requested.is_file():
        flash("Arquivo não encontrado.", "error")
        return redirect(url_for("patients.edit", patient_id=patient_id))
    return send_file(requested)


def save_patient(patient_id=None):
    profissional_id = current_professional_id()
    try:
        nome = (request.form.get("nome") or "").strip()
        sexo = Sexo(request.form.get("sexo"))
        data_nascimento = datetime.strptime(request.form.get("data_nascimento") or "", "%Y-%m-%d").date()
    except (TypeError, ValueError):
        flash("Dados do paciente inválidos.", "error")
        return redirect(request.url)

    if not nome or data_nascimento > date.today():
        flash("Informe nome, sexo e uma data de nascimento válida.", "error")
        return redirect(request.url)

    with db_session() as db:
        profissional = db.get(Profissional, profissional_id)
        if patient_id:
            paciente = professional_patient_query(db, profissional_id).filter(Paciente.id == patient_id).first()
            if not paciente:
                flash("Paciente não encontrado.", "error")
                return redirect(url_for("patients.index"))
        else:
            paciente = Paciente()

        paciente.nome = nome
        paciente.cpf = optional(request.form.get("cpf"))
        paciente.email = optional(request.form.get("email"))
        paciente.telefone = optional(request.form.get("telefone"))
        paciente.data_nascimento = data_nascimento
        paciente.sexo = sexo
        paciente.nome_social = optional(request.form.get("nome_social"))
        paciente.endereco = optional(request.form.get("endereco"))
        paciente.origem_encaminhamento = optional(request.form.get("origem_encaminhamento"))
        paciente.requisicao_medica = optional(request.form.get("requisicao_medica"))
        paciente.status_jornada = request.form.get("status_jornada") or "cadastro"
        paciente.triagem_clinica = optional(request.form.get("triagem_clinica"))
        paciente.triagem_socioeconomica = optional(request.form.get("triagem_socioeconomica"))
        paciente.caracteristicas_fisicas = optional(request.form.get("caracteristicas_fisicas"))
        paciente.consentimento_lgpd = request.form.get("consentimento_lgpd") == "on"
        paciente.observacoes_lgpd = optional(request.form.get("observacoes_lgpd"))

        if not patient_id:
            db.add(paciente)
            db.flush()
        if profissional and profissional not in paciente.profissionais:
            paciente.profissionais.append(profissional)

        _save_patient_photos(paciente)
        _sync_family_members(paciente)
        _add_uploaded_documents(paciente)
        db.commit()

    flash("Paciente salvo com sucesso.", "success")
    return redirect(url_for("patients.index"))


def optional(value):
    return (value or "").strip() or None


def _stage_label(value):
    labels = {
        "cadastro": "Cadastro",
        "recepcao_tecnica": "Recepção técnica",
        "requisicao_medica": "Requisição médica",
        "triagem": "Triagem",
        "exame": "Exame",
        "resultado": "Resultado",
        "pos_diagnostico": "Pós-diagnóstico",
    }
    return labels.get(value or "cadastro", "Cadastro")


def _professionals_label(paciente):
    if not paciente.profissionais:
        return "-"
    return ", ".join(sorted(profissional.nome for profissional in paciente.profissionais))


def _save_patient_photos(paciente):
    fields = {
        "foto_rosto": "rosto",
        "foto_perfil": "perfil",
        "foto_lado": "lado",
    }
    for field, label in fields.items():
        file = request.files.get(field)
        if not file or not file.filename:
            continue
        filename = _save_upload(paciente.id, file, label)
        setattr(paciente, field, filename)


def _sync_family_members(paciente):
    paciente.familiares.clear()
    nomes = request.form.getlist("familiar_nome")
    parentescos = request.form.getlist("familiar_parentesco")
    telefones = request.form.getlist("familiar_telefone")
    emails = request.form.getlist("familiar_email")
    momentos = request.form.getlist("familiar_momento")
    observacoes = request.form.getlist("familiar_observacao")

    for index, nome in enumerate(nomes):
        nome = optional(nome)
        if not nome:
            continue
        paciente.familiares.append(FamiliarPaciente(
            nome=nome,
            parentesco=_list_value(parentescos, index),
            telefone=_list_value(telefones, index),
            email=_list_value(emails, index),
            momento_cadastro=_list_value(momentos, index) or "pre_avaliacao",
            observacao=_list_value(observacoes, index),
        ))


def _add_uploaded_documents(paciente):
    descricoes = request.form.getlist("documento_descricao")
    tipos = request.form.getlist("documento_tipo")
    origens = request.form.getlist("documento_origem")
    files = request.files.getlist("documento_arquivo")

    for index, file in enumerate(files):
        descricao = _list_value(descricoes, index)
        if not descricao and (not file or not file.filename):
            continue
        filename = _save_upload(paciente.id, file, "documento") if file and file.filename else None
        paciente.documentos.append(DocumentoPaciente(
            descricao=descricao or "Documento anterior",
            tipo_documento=_list_value(tipos, index) or "avaliacao_anterior",
            origem=_list_value(origens, index),
            nome_arquivo=file.filename if file and file.filename else None,
            caminho_arquivo=filename,
        ))


def _save_upload(patient_id, file, label):
    uploads_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "pacientes" / str(patient_id)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename).suffix.lower()
    safe_label = secure_filename(label) or "arquivo"
    filename = f"{safe_label}-{uuid4().hex}{suffix}"
    file.save(uploads_dir / filename)
    return filename


def _list_value(values, index):
    if index >= len(values):
        return None
    return optional(values[index])
