from flask import jsonify, request, session
from . import admin_bp
from app.services.admin.videos import (
    get_pending_admin_videos,
    approve_admin_video,
    reject_admin_video,
    remove_admin_video,
)


@admin_bp.route("/videos/pending", methods=["GET"])
def admin_get_pending_videos():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        videos = get_pending_admin_videos(user_id)

        return jsonify({
            "message": "success",
            "videos": videos
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/videos/approve", methods=["PATCH"])
def admin_approve_video():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        exercise_id = data.get("exercise_id")

        video = approve_admin_video(
            user_id=user_id,
            exercise_id=exercise_id
        )

        return jsonify({
            "message": "success",
            "video": video
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/videos/reject", methods=["PATCH"])
def admin_reject_video():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        exercise_id = data.get("exercise_id")
        video_review_note = data.get("video_review_note")

        video = reject_admin_video(
            user_id=user_id,
            exercise_id=exercise_id,
            video_review_note=video_review_note
        )

        return jsonify({
            "message": "success",
            "video": video
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/videos/remove", methods=["PATCH"])
def admin_remove_video():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        exercise_id = data.get("exercise_id")

        video = remove_admin_video(
            user_id=user_id,
            exercise_id=exercise_id
        )

        return jsonify({
            "message": "success",
            "video": video
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500