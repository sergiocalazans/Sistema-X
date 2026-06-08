from functools import wraps

from flask import flash, redirect, session, url_for


ROLE_ADMIN = "admin"
ROLE_PROFESSIONAL = "profissional"
ROLE_VIEWER = "visualizador"

ROLE_LABELS = {
    ROLE_ADMIN: "Administrador",
    ROLE_PROFESSIONAL: "Profissional",
    ROLE_VIEWER: "Visualizador",
}


def current_professional_id():
    return session.get("profissional_id")


def current_user_role():
    return session.get("tipo_usuario") or ROLE_PROFESSIONAL


def current_user_role_label():
    return ROLE_LABELS.get(current_user_role(), "Profissional")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_professional_id():
            flash("Faça login para continuar.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_professional_id():
                flash("Faça login para continuar.", "error")
                return redirect(url_for("auth.login"))
            if current_user_role() not in roles:
                flash("Seu tipo de usuário não tem acesso a esta área.", "error")
                return redirect(url_for("dashboard.index"))
            return view(*args, **kwargs)

        return wrapped

    return decorator

