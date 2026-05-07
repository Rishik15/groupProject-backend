from flask import jsonify, session
from . import admin_bp
from app.services.admin.dashboard import get_dashboard_stats


def _get_session_timezone():
    return session.get("timezone") or "America/New_York"


@admin_bp.route("/dashboard/health", methods=["GET"])
def admin_health():
    """
    Check admin route health
    ---
    tags:
      - admin
    responses:
      200:
        description: Admin routes active
      401:
        description: Unauthorized
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    return (
        jsonify(
            {
                "message": "admin routes active",
                "user_id": int(user_id),
            }
        ),
        200,
    )


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

        stats = get_dashboard_stats(
            user_id=user_id,
            user_timezone=_get_session_timezone(),
        )

        return (
            jsonify(
                {
                    "message": "success",
                    "stats": stats,
                }
            ),
            200,
        )

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500
