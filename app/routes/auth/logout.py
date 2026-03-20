from . import auth_bp
from flask import session

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return {"message": "Logged out successfully"}, 200