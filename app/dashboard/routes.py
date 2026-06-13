from flask import Blueprint, redirect, render_template, url_for

from app.models import Avaliacao, Paciente, Profissional
from app.shared.auth import current_professional_id, current_user_can_view_global_data
from app.shared.db import db_session
from app.shared.formatters import assessment_view

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    profissional_id = current_professional_id()
    if not profissional_id:
        return redirect(url_for("auth.login"))

    with db_session() as db:
        if current_user_can_view_global_data():
            total_patients = db.query(Paciente).count()
            assessments_query = db.query(Avaliacao)
        else:
            total_patients = (
                db.query(Paciente)
                .join(Paciente.profissionais)
                .filter(Profissional.id == profissional_id)
                .count()
            )
            assessments_query = db.query(Avaliacao).filter(Avaliacao.profissional_id == profissional_id)

        assessments = assessments_query.order_by(Avaliacao.realizado_em.desc()).all()
        recent = [assessment_view(item) for item in assessments[:6]]

        return render_template(
            "pages/dashboard.html",
            active_page="dashboard",
            total_patients=total_patients,
            total_assessments=len(assessments),
            total_referrals=sum(1 for item in assessments if item.encaminhar),
            positive_results=sum(1 for item in assessments if item.resultado_exame == "positivo"),
            recent_assessments=recent,
        )
