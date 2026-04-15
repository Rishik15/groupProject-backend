from . import auth_bp
from app import bcrypt
from flask import request, session
from app.services.auth.checkUser import checkUserExists
from app.services.auth.client import addClient
from app.services.auth.coach import addCoach


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

    first_name, last_name = name.split(" ", 1)

    if role == "client":
        user_id = addClient(email, password_hash, first_name, last_name)

    else:
        user_id = addCoach(email, password_hash, first_name, last_name)

    session.permanent = True
    session["user_id"] = user_id
    session["role"] = role

    return {"success": True, "role": role}, 201
