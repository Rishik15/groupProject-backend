from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.assign_Client_Plan import assign_plan_to_client


@coach_bp.route("/assign", methods=["POST"])
def assign_plan_to_client_route():
    data = request.get_json()
    client_user_id = data.get("client_user_id")
    plan_id = data.get("plan_id")
    note = data.get("note")
    coach_id = session.get("user_id")

    if not coach_id:
        return jsonify({"error": "Not logged in"}), 401
    if not client_user_id or not plan_id:
        return jsonify({"error": "client_user_id and plan_id are required"}), 400

    try:
        assign_plan_to_client(
            coach_id=coach_id,
            client_user_id=client_user_id,
            plan_id=plan_id,
            note=note
        )
        return jsonify({"message": "Plan assigned to client successfully"}), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500