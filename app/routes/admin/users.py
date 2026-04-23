from flask import jsonify, request, session
from . import admin_bp
from app.services.admin.users import (
    get_admin_users,
    get_active_coaches,
    suspend_admin_user,
    deactivate_admin_user,
    update_admin_user_status,
)


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


@admin_bp.route("/users/suspend", methods=["PATCH"])
def admin_suspend_user():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        target_user_id = data.get("user_id")
        suspension_reason = data.get("suspension_reason")

        user = suspend_admin_user(
            admin_user_id=user_id,
            target_user_id=target_user_id,
            suspension_reason=suspension_reason
        )

        return jsonify({
            "message": "success",
            "user": user
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/deactivate", methods=["PATCH"])
def admin_deactivate_user():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        target_user_id = data.get("user_id")
        suspension_reason = data.get("suspension_reason")

        user = deactivate_admin_user(
            admin_user_id=user_id,
            target_user_id=target_user_id,
            suspension_reason=suspension_reason
        )

        return jsonify({
            "message": "success",
            "user": user
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except PermissionError:
        return jsonify({"error": "Forbidden"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/users/status", methods=["PATCH"])
def admin_update_user_status():
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = int(user_id)
        data = request.get_json() or {}

        target_user_id = data.get("user_id")
        account_status = data.get("account_status")
        suspension_reason = data.get("suspension_reason")

        user = update_admin_user_status(
            admin_user_id=user_id,
            target_user_id=target_user_id,
            account_status=account_status,
            suspension_reason=suspension_reason
        )

        return jsonify({
            "message": "success",
            "user": user
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

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