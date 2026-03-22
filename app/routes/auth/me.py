from . import auth_bp
from flask import session
from app.services.auth.checkUser import checkUserExists


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return {"authenticated": False}, 401

    if not checkUserExists(user_id=session.get("user_id")):
        session.clear()
        return {"authenticated": False}, 401

    return {"authenticated": True, "role": session.get("role")}, 200
