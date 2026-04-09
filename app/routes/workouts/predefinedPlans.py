from flask import jsonify, request, session
from . import workouts_bp
from app.services.workouts.predefined_Plans import get_predefined_plans


@workouts_bp.route("/predefined", methods=["POST"])
def get_predefined_plans_route():
    data = request.get_json()
    category = data.get("category")
    days_per_week = data.get("days_per_week")
    duration = data.get("duration")
    level = data.get("level")

    try:
        plans = get_predefined_plans(
            category=category,
            days_per_week=days_per_week,
            duration=duration,
            level=level
        )
        return jsonify({"plans": plans}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500