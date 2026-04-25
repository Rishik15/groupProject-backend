from flask import jsonify, request, session
from . import nutrition_bp
from app.services.nutrition.log_Meal_From_Plan import log_meal_from_plan
from datetime import datetime


@nutrition_bp.route("/meal-plans/log-meal", methods=["POST"])
def log_meal_from_plan_route():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meal_id   = request.form.get("meal_id")
    servings  = request.form.get("servings", 1.0)
    eaten_at  = request.form.get("eaten_at")
    notes     = request.form.get("notes")
    uploaded_file = request.files.get("photo")

    if not meal_id:
        return jsonify({"error": "meal_id is required"}), 400

    if not eaten_at:
        eaten_at = datetime.now().isoformat()

    try:
        photo_url = log_meal_from_plan(
            user_id=user_id,
            meal_id=int(meal_id),
            servings=float(servings),
            eaten_at=eaten_at,
            notes=notes,
            uploaded_file=uploaded_file
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Meal logged successfully",
        "photo_url": photo_url
    }), 201