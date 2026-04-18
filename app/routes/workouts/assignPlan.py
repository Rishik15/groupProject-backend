from flask import request, jsonify, session
from app.services.workouts.assign_Plan import assign_plan_to_user
from . import workouts_bp


@workouts_bp.route("/predefined/assign", methods=["POST"])
def assign_plan_route():
    data = request.get_json()

    user_id = session.get("user_id")  
    plan_id = data.get("plan_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    try:
        assign_plan_to_user(user_id=user_id, plan_id=plan_id)
        return jsonify({"message": "Plan assigned successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500