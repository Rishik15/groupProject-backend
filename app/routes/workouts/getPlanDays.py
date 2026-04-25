from flask import jsonify, request, session
from . import workouts_bp
from app.services.workouts.get_Plan_Days import get_plan_days


@workouts_bp.route("/plan-days", methods=["POST"])
def get_plan_days_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    plan_id = data.get("plan_id")

    if not plan_id:
        return jsonify({"error": "plan_id is required"}), 400

    days = get_plan_days(plan_id)

    if not days:
        return jsonify({"error": "Workout plan not found"}), 404

    return jsonify(days), 200