from flask import Blueprint

manage_bp = Blueprint("manage", __name__)

from . import getClients

from .dashboard import manage_dashboard_bp
from .nutrition import manage_nutrition_bp
from .workouts import manage_workouts_bp

manage_bp.register_blueprint(manage_dashboard_bp, url_prefix="/dashboard")
manage_bp.register_blueprint(manage_nutrition_bp, url_prefix="/nutrition")
manage_bp.register_blueprint(manage_workouts_bp, url_prefix="/workouts")
