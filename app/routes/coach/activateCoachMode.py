from flask import session
from . import coach_bp
from app.services.auth.coachApplicationActivation import activateCoachMode


@coach_bp.route("/activate-coach-mode", methods=["POST"])
def activate_coach_mode():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    user_id = int(session["user_id"])

    activateCoachMode(user_id)

    return {"success": True}, 200
