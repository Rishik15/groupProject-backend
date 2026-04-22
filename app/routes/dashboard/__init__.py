from sys import prefix

from flask import Blueprint

dashboard_bp = Blueprint("dashboard", __name__)

from .client import dashboard_client_bp

dashboard_bp.register_blueprint(dashboard_client_bp, url_prefix="/client")
