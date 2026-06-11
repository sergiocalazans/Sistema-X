from flask import Flask

from app.blueprints import register_blueprints
from app.database import init_db
from app.security import register_security_hooks
from app.services.seed_data import sync_mvp_defaults
from app.template_context import register_template_context


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    with app.app_context():
        init_db()
        sync_mvp_defaults()

    register_blueprints(app)
    register_template_context(app)
    register_security_hooks(app)

    return app
