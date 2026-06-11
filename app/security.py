from flask import redirect, request, url_for

from app.shared.auth import current_professional_id, current_user_must_update_password


def register_security_hooks(app):
    @app.before_request
    def require_password_update():
        allowed_endpoints = {
            "auth.force_password_update",
            "auth.logout",
            "static",
        }
        if not current_professional_id() or not current_user_must_update_password():
            return None
        if request.endpoint in allowed_endpoints:
            return None
        return redirect(url_for("auth.force_password_update"))
