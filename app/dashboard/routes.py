from flask import Blueprint, redirect, render_template, url_for

from app.models import Avaliacao, Paciente, Profissional
from app.shared.auth import current_professional_id, login_required
from app.shared.db import db_session
from app.shared.formatters import assessment_view

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    profissional_id = current_professional_id()
    if not profissional_id:
        return redirect(url_for("auth.login"))

    with db_session() as db:
        total_patients = (
            db.query(Paciente)
            .join(Paciente.profissionais)
            .filter(Profissional.id == profissional_id)
            .count()
        )
        assessments = (
            db.query(Avaliacao)
            .filter(Avaliacao.profissional_id == profissional_id)
            .order_by(Avaliacao.realizado_em.desc())
            .all()
        )
        recent = [assessment_view(item) for item in assessments[:6]]

        return render_template(
            "pages/dashboard.html",
            active_page="dashboard",
            total_patients=total_patients,
            total_assessments=len(assessments),
            total_referrals=sum(1 for item in assessments if item.encaminhar),
            recent_assessments=recent,
        )
