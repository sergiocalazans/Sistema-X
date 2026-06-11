from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import func
from werkzeug.security import generate_password_hash

from app.models import Avaliacao, Profissional
from app.shared.auth import ROLE_ADMIN, ROLE_LABELS, current_professional_id, role_required
from app.shared.db import db_session

users_bp = Blueprint("users", __name__, url_prefix="/usuarios")

DEFAULT_PASSWORD = "123456"
ALLOWED_ROLES = tuple(ROLE_LABELS.keys())


@users_bp.get("")
@role_required(ROLE_ADMIN)
def index():
    with db_session() as db:
        users = db.query(Profissional).order_by(Profissional.nome).all()
        return render_template(
            "pages/users.html",
            active_page="users",
            users=users,
            role_labels=ROLE_LABELS,
            default_password=DEFAULT_PASSWORD,
        )


@users_bp.post("/novo")
@role_required(ROLE_ADMIN)
def create():
    nome = (request.form.get("nome") or "").strip()
    especialidade = (request.form.get("especialidade") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    tipo_usuario = request.form.get("tipo_usuario") or "profissional"

    if not nome or not especialidade or not email:
        flash("Informe nome, especialidade e e-mail do usuário.", "error")
        return redirect(url_for("users.index"))
    if tipo_usuario not in ALLOWED_ROLES:
        flash("Tipo de usuário inválido.", "error")
        return redirect(url_for("users.index"))

    with db_session() as db:
        exists = db.query(Profissional).filter(func.lower(Profissional.email) == email).first()
        if exists:
            flash("E-mail já cadastrado para outro usuário.", "error")
            return redirect(url_for("users.index"))

        db.add(Profissional(
            nome=nome,
            email=email,
            especialidade=especialidade,
            tipo_usuario=tipo_usuario,
            senha_hash=generate_password_hash(DEFAULT_PASSWORD),
            deve_atualizar_senha=True,
        ))
        db.commit()

    flash(f"Usuário cadastrado com senha padrão {DEFAULT_PASSWORD}.", "success")
    return redirect(url_for("users.index"))


@users_bp.post("/<int:user_id>/excluir")
@role_required(ROLE_ADMIN)
def delete(user_id):
    if user_id == current_professional_id():
        flash("Você não pode excluir o próprio usuário logado.", "error")
        return redirect(url_for("users.index"))

    with db_session() as db:
        user = db.get(Profissional, user_id)
        if not user:
            flash("Usuário não encontrado.", "error")
            return redirect(url_for("users.index"))
        admin = db.get(Profissional, current_professional_id())
        if not admin:
            flash("Administrador logado não encontrado.", "error")
            return redirect(url_for("users.index"))

        for paciente in list(user.pacientes):
            if admin not in paciente.profissionais:
                paciente.profissionais.append(admin)
            paciente.profissionais.remove(user)

        (
            db.query(Avaliacao)
            .filter(Avaliacao.profissional_id == user.id)
            .update({Avaliacao.profissional_id: admin.id})
        )
        db.delete(user)
        db.commit()

    flash("Usuário excluído com sucesso. Vínculos clínicos foram preservados com o administrador logado.", "success")
    return redirect(url_for("users.index"))
