from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import Profissional
from app.shared.auth import current_professional_id, login_required
from app.shared.db import db_session

settings_bp = Blueprint("settings", __name__, url_prefix="/configuracoes")


@settings_bp.get("")
@login_required
def index():
    with db_session() as db:
        profissional = db.get(Profissional, current_professional_id())
        return render_template("pages/settings.html", active_page="settings", professional=profissional)


@settings_bp.post("/perfil")
@login_required
def profile():
    profissional_id = current_professional_id()
    nome = (request.form.get("nome") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    especialidade = (request.form.get("especialidade") or "").strip()

    if not nome or not email or not especialidade:
        flash("Preencha todos os dados de login.", "error")
        return redirect(url_for("settings.index"))

    with db_session() as db:
        exists = (
            db.query(Profissional)
            .filter(func.lower(Profissional.email) == email, Profissional.id != profissional_id)
            .first()
        )
        if exists:
            flash("E-mail já cadastrado por outro usuário.", "error")
            return redirect(url_for("settings.index"))

        profissional = db.get(Profissional, profissional_id)
        profissional.nome = nome
        profissional.email = email
        profissional.especialidade = especialidade
        db.commit()

    flash("Perfil atualizado.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.post("/senha")
@login_required
def password():
    senha_atual = request.form.get("senha_atual") or ""
    nova_senha = request.form.get("nova_senha") or ""
    confirmar_senha = request.form.get("confirmar_senha") or ""

    if len(nova_senha) < 6 or nova_senha != confirmar_senha:
        flash("Confira a nova senha e a confirmação.", "error")
        return redirect(url_for("settings.index"))

    with db_session() as db:
        profissional = db.get(Profissional, current_professional_id())
        if not profissional or not check_password_hash(profissional.senha_hash, senha_atual):
            flash("Senha atual inválida.", "error")
            return redirect(url_for("settings.index"))

        profissional.senha_hash = generate_password_hash(nova_senha)
        db.commit()

    flash("Senha atualizada.", "success")
    return redirect(url_for("settings.index"))

