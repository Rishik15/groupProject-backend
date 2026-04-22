from flask import Blueprint

dashboard_coach_bp = Blueprint("dashCoach", __name__)

from . import getMetrics
from . import getContracts
