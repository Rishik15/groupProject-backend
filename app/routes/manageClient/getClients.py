from . import manage_bp
from flask import jsonify, session
from app.services.manageClients.getClientContracts import getClientContracts


@manage_bp.route("/getClients", methods=["GET"])
def getClients():
    coach_id = session.get("user_id")

    if not coach_id:
        return "Error: Unauthorized", 404

    clients = getClientContracts(coach_id)

    return jsonify(clients)
