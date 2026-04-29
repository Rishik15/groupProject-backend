from . import contract_bp
from flask import session, request, jsonify
from app.services.contracts.contract_Status import get_contract_status

@contract_bp.route("/contractStatus", methods=["GET"])
def contractStatusRoute():
    """
Get contract status
---
tags:
  - contracts
parameters:
  - name: coach_id
    in: query
    type: integer
    required: true
responses:
  200:
    description: Contract status
  400:
    description: Missing coach_id
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    coach_id = request.args.get("coach_id")
    if not coach_id:
        return jsonify({"error": "coach_id is required"}), 400

    try:
        status = get_contract_status(user_id=user_id, coach_id=int(coach_id))
        return jsonify({"status": status}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500