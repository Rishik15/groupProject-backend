from .test import test_bp
from .auth import auth_bp
from .client import client_bp
from .topCoaches import topCoaches_bp
def register_routes(app):
    app.register_blueprint(test_bp, url_prefix="/test")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(client_bp, url_prefix="/client")
    app.register_blueprint(topCoaches_bp, url_prefix="/topCoaches")