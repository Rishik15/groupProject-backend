from flask import jsonify, session
from . import admin_bp
from app.services.admin.dashboard import get_dashboard_stats


@admin_bp.route("/dashboard/health", methods=["GET"])
def admin_health():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "message": "admin routes active",
        "user_id": int(user_id)
    }), 200


@admin_bp.route("/dashboard/stats", methods=["GET"])
def admin_dashboard_stats():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)

        stats = get_dashboard_stats(user_id)

        return jsonify({
            "message": "success",
            "stats": stats
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500