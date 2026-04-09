from flask import session, jsonify
from . import metric_bp
from app.services.metric.clientMetrics import clientMetrics


@metric_bp.route("/clientMetrics", methods=["GET"])
def getClientMetrics():
    userId = session.get("user_id")

    if not userId:
        return {"Authenticated": False}, 401

    metrics = clientMetrics(user_id = userId)

    return metrics