from . import dashboard_coach_bp
from flask import session
from app.services.auth.checkUser import checkUserExists
from app.services.dashboard.coach.getCoachContracts import getCoachContracts


@dashboard_coach_bp.route("/contracts", methods=["GET"])
def get_contracts():

    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    coach_id = session.get("user_id")

    if not checkUserExists(user_id=coach_id):
        return {"error": "Unauthorized"}, 401

    data = getCoachContracts(coach_id)

    return {
        "pending_requests": data["pending"],
        "present_contracts": data["present"],
        "history_contracts": data["history"],
        "counts": {
            "pending": len(data["pending"]),
            "present": len(data["present"]),
            "history": len(data["history"]),
        },
    }, 200
