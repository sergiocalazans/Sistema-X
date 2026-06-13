from flask import Blueprint, render_template, send_file

from app.services.pdf_reports import reports_pdf
from app.services.reports import build_reports
from app.shared.auth import ROLE_ADMIN, ROLE_PROFESSIONAL, ROLE_VIEWER, current_professional_id, current_user_can_view_global_data, role_required
from app.shared.db import db_session

reports_bp = Blueprint("reports", __name__, url_prefix="/relatorios")


@reports_bp.get("")
@role_required(ROLE_ADMIN, ROLE_PROFESSIONAL, ROLE_VIEWER)
def index():
    profissional_id = current_professional_id()
    with db_session() as db:
        reports = build_reports(db, profissional_id, include_all=current_user_can_view_global_data())
        return render_template(
            "pages/reports.html",
            active_page="reports",
            indicators=reports["indicators"],
            analyses=reports["analyses"],
            tables=reports["tables"],
            charts=reports["charts"],
        )


@reports_bp.get("/pdf")
@role_required(ROLE_ADMIN, ROLE_PROFESSIONAL, ROLE_VIEWER)
def pdf():
    profissional_id = current_professional_id()
    with db_session() as db:
        output = reports_pdf(db, profissional_id, include_all=current_user_can_view_global_data())
        return send_file(
            output,
            as_attachment=True,
            download_name="relatorio-sistema-x.pdf",
            mimetype="application/pdf",
        )

