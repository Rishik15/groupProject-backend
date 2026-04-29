from flask import session, jsonify
from . import metric_bp
from app.services.metric.clientMetrics import clientMetrics


@metric_bp.route("/clientMetrics", methods=["GET"])
def getClientMetrics():
    """
Get client metrics
---
tags:
  - metrics
responses:
  200:
    description: Metrics data
  401:
    description: Unauthorized
"""
    userId = session.get("user_id")

    if not userId:
        return {"Authenticated": False}, 401

    metrics = clientMetrics(user_id = userId)

    return metrics