from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import Profissional
from app.shared.db import db_session

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""

        with db_session() as db:
            profissional = db.query(Profissional).filter(func.lower(Profissional.email) == email).first()
            if profissional and check_password_hash(profissional.senha_hash, senha):
                session["profissional_id"] = profissional.id
                session["tipo_usuario"] = profissional.tipo_usuario
                session["deve_atualizar_senha"] = profissional.deve_atualizar_senha
                if profissional.deve_atualizar_senha:
                    return redirect(url_for("auth.force_password_update"))
                return redirect(url_for("dashboard.index"))

        flash("E-mail ou senha inválidos.", "error")

    return render_template("pages/login.html")


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def register():
    flash("O cadastro de usuários é realizado pelo administrador do sistema.", "error")
    return redirect(url_for("auth.login"))


@auth_bp.route("/atualizar-senha", methods=["GET", "POST"])
def force_password_update():
    profissional_id = session.get("profissional_id")
    if not profissional_id:
        flash("Faça login para continuar.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nova_senha = request.form.get("nova_senha") or ""
        confirmar_senha = request.form.get("confirmar_senha") or ""

        if len(nova_senha) < 6 or nova_senha != confirmar_senha:
            flash("A nova senha deve ter pelo menos 6 caracteres e coincidir com a confirmação.", "error")
            return render_template("pages/force_password_update.html")

        with db_session() as db:
            profissional = db.get(Profissional, profissional_id)
            if not profissional:
                session.clear()
                flash("Usuário não encontrado. Faça login novamente.", "error")
                return redirect(url_for("auth.login"))

            profissional.senha_hash = generate_password_hash(nova_senha)
            profissional.deve_atualizar_senha = False
            db.commit()
            session["deve_atualizar_senha"] = False

        flash("Senha atualizada com sucesso.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("pages/force_password_update.html")


@auth_bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

