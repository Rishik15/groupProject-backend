from flask import Blueprint

manage_bp = Blueprint("manage", __name__)

from . import getClients

from .dashboard import manage_dashboard_bp

manage_bp.register_blueprint(manage_dashboard_bp, url_prefix="/dashboard")
