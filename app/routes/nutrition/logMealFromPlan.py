from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.log_Meal_From_Plan import log_meal_from_plan


@nutrition_bp.route("/meal-plans/log-meal", methods=["POST"])
def log_meal_from_plan_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meal_id = request.form.get("meal_id")
    eaten_at = request.form.get("eaten_at")
    servings = request.form.get("servings", "1")
    notes = request.form.get("notes")
    photo = request.files.get("photo")

    if not meal_id:
        return jsonify({"error": "meal_id is required"}), 400

    if not eaten_at:
        return jsonify({"error": "eaten_at is required"}), 400

    try:
        photo_url = log_meal_from_plan(
            user_id=int(user_id),
            meal_id=int(meal_id),
            servings=float(servings),
            eaten_at=eaten_at,
            notes=notes,
            uploaded_file=photo,
        )

        return (
            jsonify(
                {
                    "message": "Meal logged successfully",
                    "photo_url": photo_url,
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
