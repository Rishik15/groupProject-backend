from . import dashboard_coach_bp
from flask import session
from app.services.auth.checkUser import checkUserExists
from app.services.dashboard.coach.getClientGrowth import getClientGrowthLast3Months


@dashboard_coach_bp.route("/clientGrowth", methods=["GET"])
def client_growth():

    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    coach_id = session.get("user_id")

    if not checkUserExists(user_id=coach_id):
        return {"error": "Unauthorized"}, 401

    data = getClientGrowthLast3Months(coach_id)

    return {"client_growth": data, "count": len(data)}, 200
