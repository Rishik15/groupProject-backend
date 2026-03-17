from .test import test_bp
from .auth import auth_bp


def register_routes(app):
    app.register_blueprint(test_bp, url_prefix="/test")
    app.register_blueprint(auth_bp, url_prefix="/auth")
