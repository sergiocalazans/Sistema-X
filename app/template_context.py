from app.shared.auth import current_user_role, current_user_role_label


def register_template_context(app):
    @app.context_processor
    def inject_current_user_role():
        return {
            "current_user_role": current_user_role(),
            "current_user_role_label": current_user_role_label(),
        }
