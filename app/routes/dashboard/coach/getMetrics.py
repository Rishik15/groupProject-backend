from . import dashboard_coach_bp
from flask import session
from app.services.dashboard.coach.getMetrics import get_coach_metrics


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@dashboard_coach_bp.route("/metric", methods=["GET"])
def getCoachMetrics():
    """
Get coach metrics
---
tags:
  - dashboard-coach
responses:
  200:
    description: Coach metrics
  401:
    description: Unauthorized
"""
    coach_id = session.get("user_id")

    if not coach_id:
        return {"error": "Unauthorized"}, 401

    data = get_coach_metrics(
        coach_id=int(coach_id),
        user_timezone=_get_session_timezone(),
    )

    return data, 200