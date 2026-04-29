from . import contract_bp
from flask import session, request, jsonify

from app.services.contracts.contract_Status import (
    get_contract_status,
    get_client_active_coach,
)


@contract_bp.route("/clientCoachStatus", methods=["GET"])
def clientCoachStatusRoute():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    coach_id = request.args.get("coach_id", type=int)

    if not coach_id:
        return jsonify({"error": "coach_id is required"}), 400

    try:
        status = get_contract_status(
            user_id=int(user_id),
            coach_id=int(coach_id),
        )

        active_coach = get_client_active_coach(user_id=int(user_id))

        return (
            jsonify(
                {
                    "status": status,
                    "has_active_contract": active_coach is not None,
                    "active_coach_id": (
                        active_coach["coach_id"] if active_coach else None
                    ),
                    "active_contract_id": (
                        active_coach["contract_id"] if active_coach else None
                    ),
                    "active_coach_name": (
                        active_coach["coach_name"] if active_coach else None
                    ),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
