from flask import request, jsonify
from . import exercise_bp
from app.services.exercises.search_Exercises import search_exercises

@exercise_bp.route("/search", methods=["POST"])
def search_exercises_route():
    """
Search exercises
---
tags:
  - exercise
parameters:
  - name: body
    in: body
responses:
  200:
    description: Exercise list
"""
    data = request.get_json()

    # Mapping 'equipment' from JSON to 'filters' in the service
    name = data.get("name", "")
    filters = data.get("equipment", []) # Expecting a list like ["dumbbell", "bench"]

    try:
        exercises = search_exercises(name=name, filters=filters)
        return jsonify({"exercises": exercises}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500