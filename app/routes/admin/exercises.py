from flask import jsonify, request, session
from . import admin_bp
from app.services.admin.exercises import (
    get_admin_exercises,
    create_admin_exercise,
    update_admin_exercise,
    delete_admin_exercise,
)


@admin_bp.route("/exercises", methods=["GET"])
def admin_get_exercises():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        exercises = get_admin_exercises(user_id)

        return jsonify({
            "message": "success",
            "exercises": exercises
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/exercises", methods=["POST"])
def admin_create_exercise():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        exercise_name = data.get("exercise_name")
        equipment = data.get("equipment")
        video_url = data.get("video_url")
        created_by = data.get("created_by")

        exercise = create_admin_exercise(
            user_id=user_id,
            exercise_name=exercise_name,
            equipment=equipment,
            video_url=video_url,
            created_by=created_by
        )

        return jsonify({
            "message": "success",
            "exercise": exercise
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/exercises", methods=["PATCH"])
def admin_update_exercise():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        exercise_id = data.get("exercise_id")
        exercise_name = data.get("exercise_name")
        equipment = data.get("equipment")
        video_url = data.get("video_url")

        exercise = update_admin_exercise(
            user_id=user_id,
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            equipment=equipment,
            video_url=video_url
        )

        return jsonify({
            "message": "success",
            "exercise": exercise
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/exercises", methods=["DELETE"])
def admin_delete_exercise():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        exercise_id = data.get("exercise_id")

        result = delete_admin_exercise(
            user_id=user_id,
            exercise_id=exercise_id
        )

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        message = str(e)
        if "Cannot delete or update a parent row" in message or "foreign key constraint fails" in message:
            return jsonify({"error": "Cannot delete exercise in use"}), 400
        return jsonify({"error": message}), 500