from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for

from app.models import Avaliacao, AvaliacaoSintoma, LimiarDecisao, PesoSintoma, Sintoma
from app.services.exports import assessments_workbook
from app.shared.auth import current_professional_id, login_required
from app.shared.db import db_session
from app.shared.formatters import assessment_view
from app.shared.patients import professional_patient_query

assessments_bp = Blueprint("assessments", __name__, url_prefix="/avaliacoes")


@assessments_bp.get("")
@login_required
def index():
    profissional_id = current_professional_id()
    with db_session() as db:
        avaliacoes = (
            db.query(Avaliacao)
            .filter(Avaliacao.profissional_id == profissional_id)
            .order_by(Avaliacao.realizado_em.desc())
            .all()
        )
        rows = [assessment_view(item) for item in avaliacoes]
        return render_template("pages/assessments.html", active_page="assessments", assessments=rows)


@assessments_bp.route("/nova", methods=["GET", "POST"])
@login_required
def create():
    profissional_id = current_professional_id()
    with db_session() as db:
        pacientes = professional_patient_query(db, profissional_id).order_by("nome").all()
        sintomas = db.query(Sintoma).order_by(Sintoma.categoria, Sintoma.descricao).all()

        if request.method == "POST":
            paciente_id = request.form.get("paciente_id", type=int)
            paciente = professional_patient_query(db, profissional_id).filter_by(id=paciente_id).first()
            if not paciente:
                flash("Paciente não encontrado.", "error")
                return redirect(url_for("assessments.create"))

            selected_symptoms = {int(item) for item in request.form.getlist("sintomas")}
            limiar = db.query(LimiarDecisao).filter(LimiarDecisao.sexo == paciente.sexo).first()
            if not limiar:
                flash("Limiar de decisão não cadastrado para o sexo do paciente.", "error")
                return redirect(url_for("assessments.create"))

            pesos = {
                peso.sintoma_id: peso.peso
                for peso in db.query(PesoSintoma).filter(PesoSintoma.sexo_referencia == paciente.sexo).all()
            }
            score = sum(pesos.get(sintoma.id, 0) for sintoma in sintomas if sintoma.id in selected_symptoms)
            avaliacao = Avaliacao(
                paciente_id=paciente.id,
                profissional_id=profissional_id,
                limiar_decisao_id=limiar.id,
                score_calculado=score,
                encaminhar=score >= limiar.valor,
                observacao=(request.form.get("observacao") or "").strip() or None,
            )
            db.add(avaliacao)
            db.flush()

            for sintoma in sintomas:
                db.add(AvaliacaoSintoma(
                    avaliacao_id=avaliacao.id,
                    sintoma_id=sintoma.id,
                    presente=sintoma.id in selected_symptoms,
                ))

            db.commit()
            return redirect(url_for("assessments.result", assessment_id=avaliacao.id))

        return render_template(
            "pages/triage.html",
            active_page="triage",
            patients=pacientes,
            symptoms=sintomas,
        )


@assessments_bp.get("/<int:assessment_id>/resultado")
@login_required
def result(assessment_id):
    profissional_id = current_professional_id()
    with db_session() as db:
        avaliacao = (
            db.query(Avaliacao)
            .filter(Avaliacao.id == assessment_id, Avaliacao.profissional_id == profissional_id)
            .first()
        )
        if not avaliacao:
            flash("Avaliação não encontrada.", "error")
            return redirect(url_for("assessments.index"))

        return render_template(
            "pages/result.html",
            active_page="assessments",
            assessment=assessment_view(avaliacao),
            should_refer=avaliacao.encaminhar,
            bar_width=min(avaliacao.score_calculado * 100, 100),
        )


@assessments_bp.get("/export")
@login_required
def export():
    profissional_id = current_professional_id()
    with db_session() as db:
        workbook = assessments_workbook(db, profissional_id)
        return send_file(
            workbook,
            as_attachment=True,
            download_name="historico-avaliacoes.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

