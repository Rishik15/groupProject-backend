from flask import jsonify, request, session

from . import auth_bp
from app.services.auth.settings import (
    get_account_settings,
    update_account_settings,
    update_profile_picture,
)
from app.services.media import save_user_uploaded_image


def _get_mode_from_query():
    mode = request.args.get("mode")

    if mode not in ["client", "coach", "admin"]:
        raise ValueError("mode must be client, coach, or admin")

    return mode


def _get_mode_from_json(data):
    mode = data.get("mode")

    if mode not in ["client", "coach", "admin"]:
        raise ValueError("mode must be client, coach, or admin")

    return mode


def _get_mode_from_form():
    mode = request.form.get("mode")

    if mode not in ["client", "coach", "admin"]:
        raise ValueError("mode must be client, coach, or admin")

    return mode


@auth_bp.route("/settings", methods=["GET"])
def get_settings():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        mode = _get_mode_from_query()

        settings_payload = get_account_settings(user_id=user_id, role=mode)

        return (
            jsonify(
                {
                    "message": "success",
                    "settings": settings_payload,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/settings", methods=["PATCH"])
def patch_settings():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        user_id = int(user_id)
        mode = _get_mode_from_json(data)

        update_json = dict(data)
        update_json.pop("mode", None)

        updated_settings = update_account_settings(
            user_id=user_id,
            role=mode,
            update_json=update_json,
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "settings": updated_settings,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/settings/profile-photo", methods=["POST"])
def upload_profile_photo():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        mode = _get_mode_from_form()

        photo = request.files.get("photo")

        if photo is None:
            return jsonify({"error": "photo file is required"}), 400

        try:
            upload_result = save_user_uploaded_image(
                user_id=user_id,
                uploaded_file=photo,
                category="profile_photos",
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        updated_settings = update_profile_picture(
            user_id=user_id,
            role=mode,
            photo_url=upload_result["photo_url"],
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "photo_url": upload_result["photo_url"],
                    "settings": updated_settings,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 50000
