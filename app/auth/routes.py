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
                return redirect(url_for("dashboard.index"))

        flash("E-mail ou senha inválidos.", "error")

    return render_template("pages/login.html")


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = (request.form.get("nome") or "Profissional").strip()
        especialidade = (request.form.get("especialidade") or "Saúde").strip()
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""

        if not email or not senha:
            flash("Informe e-mail e senha.", "error")
            return render_template("pages/login.html", mode="register")
        if len(senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "error")
            return render_template("pages/login.html", mode="register")

        with db_session() as db:
            exists = db.query(Profissional).filter(func.lower(Profissional.email) == email).first()
            if exists:
                flash("E-mail já cadastrado.", "error")
                return render_template("pages/login.html", mode="register")

            profissional = Profissional(
                nome=nome,
                email=email,
                senha_hash=generate_password_hash(senha),
                especialidade=especialidade,
            )
            db.add(profissional)
            db.commit()
            db.refresh(profissional)
            session["profissional_id"] = profissional.id

        return redirect(url_for("dashboard.index"))

    return render_template("pages/login.html", mode="register")


@auth_bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

