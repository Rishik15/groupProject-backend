from flask import jsonify, session
from . import admin_bp
from app.services.admin.analytics import get_admin_engagement_analytics


@admin_bp.route("/analytics/engagement", methods=["GET"])
def admin_get_engagement_analytics():
    """
Get admin engagement analytics
---
tags:
  - admin
responses:
  200:
    description: Engagement analytics data
    schema:
      type: object
      properties:
        message:
          type: string
        analytics:
          type: object
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

        analytics = get_admin_engagement_analytics(user_id)

        return jsonify({
            "message": "success",
            "analytics": analytics
        }), 200

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500