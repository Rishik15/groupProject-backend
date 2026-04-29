from flask import jsonify, request, session

from . import client_bp
from app.services.client.progress_photos import (
    create_progress_photo,
    get_progress_photos,
)
from app.services.media import save_user_uploaded_image


@client_bp.route("/progress-photo", methods=["POST"])
def upload_progress_photo():
    """
Upload progress photo
---
tags:
  - client
consumes:
  - multipart/form-data
parameters:
  - name: photo
    in: formData
    type: file
    required: true
  - name: caption
    in: formData
    type: string
  - name: taken_at
    in: formData
    type: string
responses:
  200:
    description: Photo uploaded
  401:
    description: Unauthorized
  403:
    description: Forbidden
"""
    try:
        user_id = session.get("user_id")
        role = session.get("role")

        if not user_id or not role:
            return jsonify({"error": "Unauthorized"}), 401

        if role != "client":
            return jsonify({"error": "Only clients can upload progress photos"}), 403

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

        return jsonify({
            "message": "success",
            "progress_photo_id": progress_photo_id,
            "photo_url": upload_result["photo_url"],
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@client_bp.route("/progress-photos", methods=["GET"])
def list_progress_photos():
    """
Get progress photos
---
tags:
  - client
responses:
  200:
    description: List of progress photos
  401:
    description: Unauthorized
  403:
    description: Forbidden
"""
    try:
        user_id = session.get("user_id")
        role = session.get("role")

        if not user_id or not role:
            return jsonify({"error": "Unauthorized"}), 401

        if role != "client":
            return jsonify({"error": "Only clients can access progress photos"}), 403

        user_id = int(user_id)

        photos = get_progress_photos(user_id)

        return jsonify({
            "message": "success",
            "progressPhotos": photos if photos is not None else [],
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500