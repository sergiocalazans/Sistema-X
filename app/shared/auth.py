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


def current_user_can_view_global_data():
    return current_user_role() in {ROLE_ADMIN, ROLE_VIEWER}


def current_user_must_update_password():
    return bool(session.get("deve_atualizar_senha"))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_professional_id():
            flash("Faça login para continuar.", "error")
            return redirect(url_for("auth.login"))
        if current_user_must_update_password():
            return redirect(url_for("auth.force_password_update"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_professional_id():
                flash("Faça login para continuar.", "error")
                return redirect(url_for("auth.login"))
            if current_user_must_update_password():
                return redirect(url_for("auth.force_password_update"))
            # A autorização fica centralizada para manter as regras de perfil iguais em todas as rotas.
            if current_user_role() not in roles:
                flash("Seu tipo de usuário não tem acesso a esta área.", "error")
                return redirect(url_for("dashboard.index"))
            return view(*args, **kwargs)

        return wrapped

    return decorator

