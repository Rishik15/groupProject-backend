from . import auth_bp
from flask import session
from app.services.auth.checkUser import checkUserExists
from app.services.auth.getUser import getUserInfo, getUserOnboardingStatus
from app.services.auth.getUserRoles import getUserRoles


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return {"authenticated": False}, 401

    user_id = session.get("user_id")
    role = session.get("role")

    if not checkUserExists(user_id=user_id):
        session.clear()
        return {"authenticated": False}, 401

    user = getUserInfo(user_id)
    needs_onboarding = getUserOnboardingStatus(user_id, role)
    roles = getUserRoles(user_id)

    return {
        "authenticated": True,
        "roles": roles,
        "user": user,
        "needs_onboarding": needs_onboarding,
    }, 200
