from . import auth_bp
from app import bcrypt
from flask import request, session
from app.services.auth.checkUser import checkUserExists
from app.services.auth.client import addClient, initialize_client_role
from app.services.auth.coach import addCoach, initialize_coach_role
from app.services.auth.getUser import getUserInfo, getUserOnboardingStatus
from app.services.auth.getUserRoles import getUserRoles


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    role = data.get("role")

    if checkUserExists(email=email):
        return {"error": "User already exists"}, 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    name_parts = name.strip().split()

    if len(name_parts) == 1:
        first_name = name_parts[0]
        last_name = ""
    else:
        first_name = " ".join(name_parts[:-1])
        last_name = name_parts[-1]

    if role == "client":
        user_id = addClient(email, password_hash, first_name, last_name)
    else:
        user_id = addCoach(email, password_hash, first_name, last_name)

    session.permanent = True
    session["user_id"] = user_id
    session["role"] = role

    roles = getUserRoles(user_id)
    user_info = getUserInfo(user_id)

    return {"success": True, "roles": roles, "user": user_info}, 200


@auth_bp.route("/updateRole", methods=["POST"])
def update_role():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    data = request.get_json() or {}
    role = data.get("role")

    if role not in {"client", "coach"}:
        return {"error": "role must be 'client' or 'coach'"}, 400

    user_id = int(session["user_id"])

    if role == "client":
        initialize_client_role(user_id, commit=True)
    else:
        initialize_coach_role(user_id, commit=True)

    session["role"] = role

    user = getUserInfo(user_id)
    needs_onboarding = getUserOnboardingStatus(user_id, role)
    roles = getUserRoles(user_id)

    return {
        "authenticated": True,
        "role": role,
        "roles": roles,
        "user": user,
        "needs_onboarding": needs_onboarding,
    }, 200
