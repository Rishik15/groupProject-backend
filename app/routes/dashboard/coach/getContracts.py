from . import dashboard_coach_bp
from flask import session
from app.services.dashboard.coach.getPendingContracts import get_pending_requests


@dashboard_coach_bp.route("/pending-requests", methods=["GET"])
def getPendingRequests():
    coach_id = session.get("user_id")

    if not coach_id:
        return {"error": "Unauthorized"}, 401

    data = get_pending_requests(coach_id)

    return {"requests": data}, 200
