from . import dashboard_coach_bp
from flask import session
from app.services.dashboard.coach.getMetrics import get_coach_metrics


@dashboard_coach_bp.route("/metric", methods=["GET"])
def getCoachMetrics():
    coach_id = session.get("user_id")

    if not coach_id:
        return {"error": "Unauthorized"}, 401

    data = get_coach_metrics(coach_id)

    return data, 200
