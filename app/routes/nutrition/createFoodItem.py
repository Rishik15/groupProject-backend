from flask import jsonify, request, session
from app.routes.nutrition import nutrition_bp
from app.services.nutrition.create_Food_Item import create_food_item
from app.services.media_storage import save_meal_image_for_user


@nutrition_bp.route("/food-items/create", methods=["POST"])
def create_food_item_route():
    """
Create food item
---
tags:
  - nutrition
consumes:
  - multipart/form-data
parameters:
  - name: name
    in: formData
    type: string
    required: true
  - name: calories
    in: formData
    type: number
    required: true
  - name: protein
    in: formData
    type: number
    required: true
  - name: carbs
    in: formData
    type: number
    required: true
  - name: fats
    in: formData
    type: number
    required: true
  - name: image
    in: formData
    type: file
responses:
  201:
    description: Food item created
  400:
    description: Invalid input
  401:
    description: Unauthorized
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    name      = request.form.get("name")
    calories  = request.form.get("calories")
    protein   = request.form.get("protein")
    carbs     = request.form.get("carbs")
    fats      = request.form.get("fats")

    if name is None or name == "":
        return jsonify({"error": "name is required"}), 400

    if calories is None:
        return jsonify({"error": "calories is required"}), 400

    if protein is None:
        return jsonify({"error": "protein is required"}), 400

    if carbs is None:
        return jsonify({"error": "carbs is required"}), 400

    if fats is None:
        return jsonify({"error": "fats is required"}), 400


    image_url = None
    uploaded_file = request.files.get("image")
    if uploaded_file:
        try:
            result = save_meal_image_for_user(user_id, uploaded_file)
            image_url = result["photo_url"]
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    try:
        create_food_item(
            user_id=user_id,
            name=name,
            calories=int(calories),
            protein=float(protein),
            carbs=float(carbs),
            fats=float(fats),
            image_url=image_url
        )
    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": f"Food item '{name}' already exists"}), 409
        return jsonify({"error": "Failed to create food item"}), 500

    return jsonify({"message": "Food item created successfully"}), 201