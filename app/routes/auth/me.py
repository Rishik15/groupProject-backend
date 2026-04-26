from . import auth_bp
from flask import session
from app.services.auth.checkUser import checkUserExists
from app.services.auth.getUser import getUserInfo, getUserOnboardingStatus
from app.services.auth.getUserRoles import getUserRoles
from app.services.auth.coachApplicationStatus import getCoachApplicationStatus
from app.services.auth.coachApplicationActivation import getCoachModeActivated


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return {"authenticated": False}, 401

    user_id = session.get("user_id")

    if not checkUserExists(user_id=user_id):
        print("AUTH ME CHECK USER FAILED:", user_id)
        return {"authenticated": False}, 401

    user_id = int(user_id)

    roles = getUserRoles(user_id)
    user = getUserInfo(user_id)
    coach_application_status = getCoachApplicationStatus(user_id)
    coach_mode_activated = getCoachModeActivated(user_id)

    active_role = None

    if "admin" in roles:
        active_role = "admin"
    elif "coach" in roles:
        active_role = "coach"
    elif "client" in roles:
        active_role = "client"

    needs_onboarding = False

    if active_role:
        needs_onboarding = getUserOnboardingStatus(user_id, active_role)

    print("AUTH ME USER:", user_id)
    print("AUTH ME ROLES:", roles)
    print("AUTH ME COACH APPLICATION STATUS:", coach_application_status)

    return {
        "authenticated": True,
        "roles": roles,
        "user": user,
        "coach_application_status": coach_application_status,
        "coach_mode_activated": coach_mode_activated,
        "needs_onboarding": needs_onboarding,
    }, 200
