from flask import Blueprint

metric_bp = Blueprint("metric", __name__)

from . import ClientDailyMetric
