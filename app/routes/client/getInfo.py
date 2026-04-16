#written by albi
from . import client_bp
from flask import session
from app.services.auth.checkUser import checkUserExists
from app.services.client.getUserInfo import getUserInfo


@client_bp.route("/getInfo", methods=["GET"])
def getInfo():
    if "user_id" not in session:
        return {"authenticated": False}, 401

    if not checkUserExists(user_id=session.get("user_id")):
        session.clear()
        return {"authenticated": False}, 401

    user = getUserInfo(session.get("user_id"))

    return {
        "user": user,
    }, 200