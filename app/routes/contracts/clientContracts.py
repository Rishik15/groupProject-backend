#app/routes/contracts/clientContracts.py
from . import contract_bp
from flask import session, request, jsonify
from app.services.contracts.client_Contracts import requestContract


@contract_bp.route("/requestContract", methods=["POST"])
def requestContractRoute():
    data = request.get_json()
    user_id = session.get("user_id") 
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    
    coach_id = data.get("coach_id")

    if not coach_id:
        return jsonify({"error": "coach_id is required"}), 400

    try:
        requestContract(user_id=user_id, coach_id=coach_id)
        return jsonify({"message": "Contract request sent successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500