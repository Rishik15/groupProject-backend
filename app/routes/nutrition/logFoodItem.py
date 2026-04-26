from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.log_Food_Item import log_food_item
import traceback


@nutrition_bp.route("/log-food-item", methods=["POST"])
def log_food_item_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    name = request.form.get("name")
    calories = request.form.get("calories")
    protein = request.form.get("protein")
    carbs = request.form.get("carbs")
    fats = request.form.get("fats")
    servings = request.form.get("servings", "1")
    eaten_at = request.form.get("eaten_at")
    notes = request.form.get("notes")
    photo = request.files.get("photo")

    if not name:
        return jsonify({"error": "name is required"}), 400

    if calories is None:
        return jsonify({"error": "calories is required"}), 400

    if protein is None:
        return jsonify({"error": "protein is required"}), 400

    if carbs is None:
        return jsonify({"error": "carbs is required"}), 400

    if fats is None:
        return jsonify({"error": "fats is required"}), 400

    if not eaten_at:
        return jsonify({"error": "eaten_at is required"}), 400

    try:
        parsed_servings = float(servings)

        if parsed_servings <= 0:
            return jsonify({"error": "servings must be greater than 0"}), 400

        result = log_food_item(
            user_id=int(user_id),
            name=name.strip(),
            calories=int(float(calories)),
            protein=float(protein),
            carbs=float(carbs),
            fats=float(fats),
            servings=parsed_servings,
            eaten_at=eaten_at,
            notes=notes,
            uploaded_file=photo,
        )

        return (
            jsonify(
                {
                    "message": "Food item logged successfully",
                    "food_item_id": result["food_item_id"],
                    "photo_url": result["photo_url"],
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        print("ERROR IN /nutrition/log-food-item")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
