from flask import Blueprint

activity_log_bp = Blueprint("activity_log", __name__)

from . import activityLogRoutes