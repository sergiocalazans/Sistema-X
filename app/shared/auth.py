from functools import wraps

from flask import flash, redirect, session, url_for


def current_professional_id():
    return session.get("profissional_id")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_professional_id():
            flash("Faça login para continuar.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped

