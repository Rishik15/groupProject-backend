from . import dashboard_client_bp
from flask import session, request
from app.services.dashboard.client.getUserMetrics import userMetrics


@dashboard_client_bp.route("/metrics", methods=["GET"])
def getMetrics():
    """
Get user metrics
---
tags:
  - dashboard-client
responses:
  200:
    description: User metrics
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Unauthorized"}, 401

    return userMetrics(user_id), 200
