from . import auth_bp
from flask import session


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if "user_id" not in session:
        return {"message": "No active session"}, 400

    session.clear()
    return {"message": "Logged out successfully"}, 200
