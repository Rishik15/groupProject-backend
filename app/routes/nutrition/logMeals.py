from . import nutrition_bp
from flask import request, session, jsonify
from app.services.nutrition import mealLogging

@nutrition_bp.route("/updateFoodItem", methods=["PATCH"])
def updateFoodItem(): 
    try:
        u_id = session.get("user_id")
        data = request.get_json() 
        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401
 
        u_id = int(u_id)

        """
        All of the following fields are required from the frontend 
        you can populate unchanged entries in the json object using the current value of the 
        food item

        data = 

        json { 
        "food_id": int   (default = /getFoodItems @ "food_id")       
        "name": str      (default = /getFoodItems @ "name")   
        "calories": int  (default = /getFoodItems @ "calories")           
        "protein": int   (default = /getFoodItems @ "protein")       
        "carbs": int     (default = /getFoodItems @ "carbs")       
        "fats": int      (default = /getFoodItems @ "fats")           
        "image_url": str (default = /getFoodItems @ "image_url")       
        
        }         

        
        localhost:8080/nutrition/updateFoodItem
        
        """
        
        fid         = data.get("food_id")
        name        = data.get("name")
        cals        = data.get("calories")
        protein     = data.get("protein")
        carbs       = data.get("carbs")
        fats        = data.get("fats")
        image_u     = data.get("image_url")
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
                                        image_u)
    
    except Exception as e:
        raise e


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
        raise e


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
        raise e


@nutrition_bp.route("/logMeal", methods=["POST"])
def logMeal():
    try:
        u_id = session.get("user_id")

        if not u_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        u_id = int(u_id)

        meal_name = data.get("name")
        eaten_at = data.get("eaten_at")
        servings = data.get("servings")
        notes = data.get("notes")
        photo_url = data.get("photo_url")
        food_item_ids = data.get("food_item_ids", [])

        req_fields = [meal_name, eaten_at, servings, photo_url]
        for r in req_fields:
            if r is None:
                return jsonify({"error": "one of the required fields was not provided"}), 400

        if not isinstance(food_item_ids, list) or len(food_item_ids) == 0:
            return jsonify({"error": "food_item_ids must be a non-empty list"}), 400

        mealLogging.mealLogInsert(
            user_id=u_id,
            meal_name=meal_name,
            eaten_at=eaten_at,
            servings=servings,
            notes=notes,
            photo_url=photo_url,
            food_item_ids=food_item_ids
        )

        return jsonify({"message": "success"}), 200

    except Exception as e:
        raise e


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
        raise e