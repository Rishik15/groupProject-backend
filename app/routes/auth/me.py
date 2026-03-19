from . import auth_bp
from flask import session

@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return {"authenticated": False}, 401

    return {
        "authenticated": True,
        "role": session["role"]
    }, 200