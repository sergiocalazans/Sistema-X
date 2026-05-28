from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

from app.models import Paciente, Profissional, Sexo
from app.services.exports import patients_workbook
from app.shared.auth import current_professional_id, login_required
from app.shared.db import db_session
from app.shared.formatters import patient_last_assessment, patient_last_score, recommendation_key, sex_label
from app.shared.patients import professional_patient_query

patients_bp = Blueprint("patients", __name__, url_prefix="/pacientes")


@patients_bp.get("")
@login_required
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
                "cpf": paciente.cpf or "-",
                "email": paciente.email or "-",
                "phone": paciente.telefone or "-",
                "sex": sex_label(paciente.sexo),
                "age": paciente.idade,
                "score": patient_last_score(paciente),
                "recommendation_key": recommendation_key(ultima.encaminhar) if ultima else "nao-prio",
            })

        return render_template("pages/patients.html", active_page="patients", patients=rows)


@patients_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        return save_patient()
    return render_template("pages/patient_form.html", active_page="patients", patient=None)


@patients_bp.route("/<int:patient_id>/editar", methods=["GET", "POST"])
@login_required
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
@login_required
def export():
    profissional_id = current_professional_id()
    with db_session() as db:
        workbook = patients_workbook(db, profissional_id)
        return send_file(
            workbook,
            as_attachment=True,
            download_name="pacientes.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


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

        if not patient_id:
            db.add(paciente)
        if profissional and profissional not in paciente.profissionais:
            paciente.profissionais.append(profissional)

        db.commit()

    flash("Paciente salvo com sucesso.", "success")
    return redirect(url_for("patients.index"))


def optional(value):
    return (value or "").strip() or None
