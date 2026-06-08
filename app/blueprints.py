def register_blueprints(app):
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
