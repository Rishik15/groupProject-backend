from .test import test_bp
from .client import client_bp

def register_routes(app):
    app.register_blueprint(test_bp, url_prefix="/test")
    app.register_blueprint(client_bp, url_prefix="/client")