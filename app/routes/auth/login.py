from . import auth_bp
from app import bcrypt
from flask import session, request
from app.services.auth.getUser import getUserCreds, getUserInfo
from app.services.auth.getUserRoles import getUserRoles
from app.services.auth.coachApplicationStatus import getCoachApplicationStatus


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login
    ---
    tags:
      - auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [email, password]
            properties:
              email:
                type: string
              password:
                type: string
    responses:
      200:
        description: Login successful
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                roles:
                  type: array
                  items:
                    type: string
                user:
                  type: object
                coach_application_status:
                  type: object
      401:
        description: Invalid credentials
    """
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    user = getUserCreds(email)

    if not user:
        return {"error": "Invalid credentials"}, 401

    if not bcrypt.check_password_hash(user["password_hash"], password):
        return {"error": "Invalid credentials"}, 401

    user_id = int(user["user_id"])

    session.permanent = True
    session["user_id"] = user_id
    session["role"] = user["role"]

    roles = getUserRoles(user_id)
    user_info = getUserInfo(user_id)
    coach_application_status = getCoachApplicationStatus(user_id)

    return {
        "success": True,
        "roles": roles,
        "user": user_info,
        "coach_application_status": coach_application_status,
    }, 200
