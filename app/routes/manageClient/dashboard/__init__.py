from flask import Blueprint

manage_dashboard_bp = Blueprint("dashboard_bp", __name__)

from . import dashboardRoutes
