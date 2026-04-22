import json

from flask import request, session, jsonify

from . import nutrition_bp
from app.services.media import save_meal_image_for_user
from app.services.nutrition import mealLogging


def _parse_food_item_ids(raw_value):
    if raw_value is None:
        return []

    if isinstance(raw_value, list):
        return [int(v) for v in raw_value]

    if isinstance(raw_value, str):
        raw_value = raw_value.strip()

        if not raw_value:
            return []

        try:
            parsed = json.loads(raw_value)
            if isinstance(parsed, list):
                return [int(v) for v in parsed]
        except json.JSONDecodeError:
            pass

        return [int(v.strip()) for v in raw_value.split(",") if v.strip()]

    raise ValueError("food_item_ids must be a list, JSON array string, or comma-separated string")


@nutrition_bp.route("/updateFoodItem", methods=["PATCH"])
def updateFoodItem():
    try:
        u_id = session.get("user_id")
        data = request.get_json()

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        u_id = int(u_id)

        fid = data.get("food_id")
        name = data.get("name")
        cals = data.get("calories")
        protein = data.get("protein")
        carbs = data.get("carbs")
        fats = data.get("fats")
        image_u = data.get("image_url")

        required_fields = [fid, name, cals, protein, carbs, fats, image_u]
        if any(v is None for v in required_fields):
            return jsonify({"error": "missing required fields"}), 400

        mealLogging.partialFoodItemUpdate(
            u_id,
            fid,
            name,
            cals,
            protein,
            carbs,
            fats,
            image_u,
        )

        return jsonify({"message": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@nutrition_bp.route("/getFoodItems", methods=["GET"])
def getUserFoodItem():
    try:
        u_id = session.get("user_id")

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        u_id = int(u_id)
        foodItemsList = mealLogging.getFoodItem(u_id)

        return jsonify({
            "message": "success",
            "foodItemsList": foodItemsList if foodItemsList is not None else []
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@nutrition_bp.route("/createFoodItem", methods=["POST"])
def addUserFoodItem():
    try:
        u_id = session.get("user_id")

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        u_id = int(u_id)

        name = data.get("name")
        cals = data.get("calories")
        pro = data.get("protein")
        carbs = data.get("carbs")
        fats = data.get("fats")
        img = data.get("image_url")

        req_fields = [name, cals, pro, carbs, fats, img]
        for r in req_fields:
            if r is None:
                return jsonify({"error": "one of the required fields was not provided"}), 400

        mealLogging.createFoodItem(
            user_id=u_id,
            name=name,
            cals=cals,
            pro=pro,
            carbs=carbs,
            fats=fats,
            img=img
        )

        return jsonify({"message": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@nutrition_bp.route("/logMeal", methods=["POST"])
def logMeal():
    try:
        u_id = session.get("user_id")

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        u_id = int(u_id)

        meal_name = request.form.get("name")
        eaten_at = request.form.get("eaten_at")
        servings_raw = request.form.get("servings")
        notes = request.form.get("notes")
        food_item_ids_raw = request.form.get("food_item_ids")
        photo = request.files.get("photo")

        if meal_name is None or eaten_at is None or servings_raw is None:
            return jsonify({"error": "name, eaten_at, and servings are required"}), 400

        if photo is None:
            return jsonify({"error": "photo file is required"}), 400

        try:
            servings = int(servings_raw)
        except ValueError:
            return jsonify({"error": "servings must be an integer"}), 400

        try:
            food_item_ids = _parse_food_item_ids(food_item_ids_raw)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if len(food_item_ids) == 0:
            return jsonify({"error": "food_item_ids must be a non-empty list"}), 400

        try:
            upload_result = save_meal_image_for_user(
                user_id=u_id,
                uploaded_file=photo,
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        mealLogging.mealLogInsert(
            user_id=u_id,
            meal_name=meal_name,
            eaten_at=eaten_at,
            servings=servings,
            notes=notes,
            photo_url=upload_result["photo_url"],
            food_item_ids=food_item_ids,
        )

        return jsonify({
            "message": "success",
            "photo_url": upload_result["photo_url"],
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@nutrition_bp.route("/getLoggedMeals", methods=["POST"])
def getLoggedMeals():
    try:
        u_id = session.get("user_id")

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        u_id = int(u_id)

        start_dt = data.get("start_datetime")
        end_dt = data.get("end_datetime")

        meals = mealLogging.getLoggedMeals(
            user_id=u_id,
            start_dt=start_dt,
            end_dt=end_dt
        )

        return jsonify({
            "message": "success",
            "loggedMeals": meals if meals is not None else []
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500