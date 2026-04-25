from flask import jsonify, request, session
from . import nutrition_bp
from app.services.nutrition import mealLogging
from datetime import datetime


@nutrition_bp.route("/weekly-calories", methods=["POST"])
def get_weekly_calories():
    try:
        u_id = session.get("user_id")

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        u_id = int(u_id)

        start_dt = data.get("start_datetime")
        end_dt = data.get("end_datetime")

        if not start_dt or not end_dt:
            return jsonify({"error": "start_datetime and end_datetime are required"}), 400

        meals = mealLogging.getLoggedMeals(
            user_id=u_id, start_dt=start_dt, end_dt=end_dt
        )

        if meals is None:
            meals = []

        # Group calories by date
        daily = {}
        for meal in meals:
            eaten_at = meal.get("eaten_at", "")
            date_key = eaten_at[:10]  # YYYY-MM-DD
            servings = float(meal.get("servings") or 1)
            calories = float(meal.get("calories") or 0)

            if date_key not in daily:
                daily[date_key] = 0.0

            daily[date_key] += calories * servings

        # Build ordered list
        days = []
        for date_str, cals in sorted(daily.items()):
            days.append({
                "date": date_str,
                "calories": round(cals)
            })

        return jsonify({
            "message": "success",
            "days": days
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500