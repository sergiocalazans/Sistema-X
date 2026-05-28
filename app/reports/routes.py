from flask import Blueprint, render_template

from app.services.reports import build_reports
from app.shared.auth import current_professional_id, login_required
from app.shared.db import db_session

reports_bp = Blueprint("reports", __name__, url_prefix="/relatorios")


@reports_bp.get("")
@login_required
def index():
    profissional_id = current_professional_id()
    with db_session() as db:
        reports = build_reports(db, profissional_id)
        return render_template(
            "pages/reports.html",
            active_page="reports",
            indicators=reports["indicators"],
            tables=reports["tables"],
            charts=reports["charts"],
        )

