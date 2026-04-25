from . import contract_bp
from flask import session, request, jsonify
from app.services.contracts.client_Contracts import (
    requestContract,
    get_client_active_contract,
)


@contract_bp.route("/clientCoachStatus", methods=["GET"])
def clientCoachStatusRoute():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    active_contract = get_client_active_contract(user_id)

    return (
        jsonify(
            {
                "has_active_contract": active_contract is not None,
                "active_coach_id": (
                    active_contract["coach_id"] if active_contract else None
                ),
            }
        ),
        200,
    )


@contract_bp.route("/requestContract", methods=["POST"])
def requestContractRoute():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json() or {}

    coach_id = data.get("coach_id")
    training_reason = data.get("training_reason", "")
    goals = data.get("goals", "")
    preferred_schedule = data.get("preferred_schedule", "")
    notes = data.get("notes", "")

    if not coach_id:
        return jsonify({"error": "coach_id is required"}), 400

    if not training_reason.strip():
        return jsonify({"error": "training reason is required"}), 400

    if not goals.strip():
        return jsonify({"error": "goals are required"}), 400

    try:
        requestContract(
            user_id=user_id,
            coach_id=coach_id,
            training_reason=training_reason,
            goals=goals,
            preferred_schedule=preferred_schedule,
            notes=notes,
        )

        return jsonify({"message": "Contract request sent successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
