from . import dashboard_coach_bp
from flask import session
from app.services.auth.checkUser import checkUserExists
from app.services.dashboard.coach.getPendingContracts import getPendingRequests


@dashboard_coach_bp.route("/pendingRequests", methods=["GET"])
def pending_requests():

    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    coach_id = session.get("user_id")

    if not checkUserExists(user_id=coach_id):
        session.clear()
        return {"error": "Unauthorized"}, 401

    requests = getPendingRequests(coach_id)

    return {"pending_requests": requests, "count": len(requests)}, 200
