from flask import jsonify, session
from . import admin_bp
from app.services.admin.users import get_admin_users, get_active_coaches


@admin_bp.route("/users", methods=["GET"])
def admin_get_users():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        users = get_admin_users(user_id)

        return jsonify({
            "message": "success",
            "users": users
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/coaches/active", methods=["GET"])
def admin_get_active_coaches():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        coaches = get_active_coaches(user_id)

        return jsonify({
            "message": "success",
            "coaches": coaches
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500