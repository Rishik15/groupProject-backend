from . import auth_bp
from app import bcrypt
from flask import session, request
from app.services.auth.checkUser import checkUserExists
from app.services.auth.getUser import getUserCreds


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = getUserCreds(email)

    if not user:
        return {"error": "Invalid credentials"}, 401

    if not bcrypt.check_password_hash(user["password_hash"], password):
        return {"error": "Invalid credentials"}, 401

    session.permanent = True
    session["user_id"] = user["user_id"]
    session["role"] = user["role"]

    return {"success": True, "role": user["role"]}, 200
