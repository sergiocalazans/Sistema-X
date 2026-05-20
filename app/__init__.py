from flask import Flask

from app.models import (
    Avaliacao,
    AvaliacaoSintoma,
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

    from app.controllers.main import main_bp

    app.register_blueprint(main_bp)

    return app
