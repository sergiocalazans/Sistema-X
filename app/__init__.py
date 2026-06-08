from flask import Flask

from app.models import (
    Avaliacao,
    AvaliacaoSintoma,
    DocumentoPaciente,
    FamiliarPaciente,
    LimiarDecisao,
    Paciente,
    PesoSintoma,
    Profissional,
    Sexo,
    Sintoma,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    from app.database import init_db
    from app.services.seed_data import sync_mvp_defaults

    with app.app_context():
        init_db()
        sync_mvp_defaults()

    from app.assessments import assessments_bp
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.patients import patients_bp
    from app.reports import reports_bp
    from app.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(assessments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    from app.shared.auth import current_user_role, current_user_role_label

    @app.context_processor
    def inject_current_user_role():
        return {
            "current_user_role": current_user_role(),
            "current_user_role_label": current_user_role_label(),
        }

    return app
