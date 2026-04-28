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
    """
Get admin dashboard statistics
---
tags:
  - admin
responses:
  200:
    description: Dashboard stats
    schema:
      type: object
      properties:
        message:
          type: string
        stats:
          type: object
          properties:
            total_users:
              type: integer
            active_coaches:
              type: integer
            pending_reviews:
              type: integer
            pending_coach_applications:
              type: integer
            open_reports:
              type: integer
            monthly_revenue:
              type: number
  401:
    description: Unauthorized
  403:
    description: Forbidden
    """
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