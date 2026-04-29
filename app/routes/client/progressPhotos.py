from flask import jsonify, request, session

from . import client_bp
from app.services.client.progress_photos import (
    create_progress_photo,
    get_progress_photos,
)
from app.services.media import save_user_uploaded_image


def _validate_client_mode(mode):
    if mode != "client":
        raise PermissionError("Only clients can access progress photos")


@client_bp.route("/progress-photo", methods=["POST"])
def upload_progress_photo():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        mode = request.form.get("mode")
        _validate_client_mode(mode)

        user_id = int(user_id)

        photo = request.files.get("photo")
        caption = request.form.get("caption")
        taken_at = request.form.get("taken_at")

        if photo is None:
            return jsonify({"error": "photo file is required"}), 400

        try:
            upload_result = save_user_uploaded_image(
                user_id=user_id,
                uploaded_file=photo,
                category="progress_photos",
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        progress_photo_id = create_progress_photo(
            user_id=user_id,
            photo_url=upload_result["photo_url"],
            caption=caption,
            taken_at=taken_at,
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "progress_photo_id": progress_photo_id,
                    "photo_url": upload_result["photo_url"],
                }
            ),
            200,
        )

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@client_bp.route("/progress-photos", methods=["GET"])
def list_progress_photos():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        mode = request.args.get("mode")
        _validate_client_mode(mode)

        user_id = int(user_id)

        photos = get_progress_photos(user_id)

        return (
            jsonify(
                {
                    "message": "success",
                    "progressPhotos": photos if photos is not None else [],
                }
            ),
            200,
        )

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500
