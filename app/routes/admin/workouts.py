from flask import jsonify, request, session
from . import admin_bp
from app.services.admin.workouts import (
    get_admin_workouts,
    create_admin_workout,
    update_admin_workout,
    delete_admin_workout,
    update_admin_workout_exercises,
)


@admin_bp.route("/workouts", methods=["GET"])
def admin_get_workouts():
    """
Get all admin workouts
---
tags:
  - admin-workouts
responses:
  200:
    description: Workouts list
  401:
    description: Unauthorized
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        workouts = get_admin_workouts(user_id)

        return jsonify({
            "message": "success",
            "workouts": workouts
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/workouts", methods=["POST"])
def admin_create_workout():
    """
Create workout (admin)
---
tags:
  - admin-workouts
parameters:
  - name: body
    in: body
    schema:
      type: object
      properties:
        plan_name: { type: string }
        description: { type: string }
        author_user_id: { type: integer }
        is_public: { type: integer }
        exercises:
          type: array
responses:
  201:
    description: Workout created
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        plan_name = data.get("plan_name")
        description = data.get("description")
        author_user_id = data.get("author_user_id")
        is_public = data.get("is_public", 0)
        exercises = data.get("exercises", [])

        workout = create_admin_workout(
            user_id=user_id,
            plan_name=plan_name,
            description=description,
            author_user_id=author_user_id,
            is_public=is_public,
            exercises=exercises
        )

        return jsonify({
            "message": "success",
            "workout": workout
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/workouts", methods=["PATCH"])
def admin_update_workout():
    """
Update workout (admin)
---
tags:
  - admin-workouts
parameters:
  - name: body
    in: body
    schema:
      type: object
      properties:
        plan_id: { type: integer }
responses:
  200:
    description: Workout updated
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        plan_id = data.get("plan_id")
        plan_name = data.get("plan_name")
        description = data.get("description")
        is_public = data.get("is_public")

        workout = update_admin_workout(
            user_id=user_id,
            plan_id=plan_id,
            plan_name=plan_name,
            description=description,
            is_public=is_public
        )

        return jsonify({
            "message": "success",
            "workout": workout
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/workouts", methods=["DELETE"])
def admin_delete_workout():
    """
Delete workout (admin)
---
tags:
  - admin-workouts
parameters:
  - name: body
    in: body
    schema:
      type: object
      required: [plan_id]
responses:
  200:
    description: Workout deleted
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        plan_id = data.get("plan_id")

        result = delete_admin_workout(
            user_id=user_id,
            plan_id=plan_id
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/workouts/exercises", methods=["PATCH"])
def admin_update_workout_exercises_route():
    """
Update workout exercises
---
tags:
  - admin-workouts
parameters:
  - name: body
    in: body
    schema:
      type: object
      required: [plan_id]
responses:
  200:
    description: Exercises updated
"""
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        plan_id = data.get("plan_id")
        exercises = data.get("exercises", [])

        workout = update_admin_workout_exercises(
            user_id=user_id,
            plan_id=plan_id,
            exercises=exercises
        )

        return jsonify({
            "message": "success",
            "workout": workout
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500