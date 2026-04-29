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
    """
Get all users (admin only)
---
tags:
  - admin
responses:
  200:
    description: List of users
    schema:
      type: object
      properties:
        message:
          type: string
        users:
          type: array
          items:
            type: object
            properties:
              user_id:
                type: integer
              first_name:
                type: string
              last_name:
                type: string
              name:
                type: string
              email:
                type: string
              phone_number:
                type: string
              is_coach:
                type: boolean
              is_admin:
                type: boolean
              account_status:
                type: string
              suspension_reason:
                type: string
              updated_at:
                type: string
                format: date-time
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
    """
Suspend a user (admin only)
---
tags:
  - admin
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - user_id
        - suspension_reason
      properties:
        user_id:
          type: integer
        suspension_reason:
          type: string
responses:
  200:
    description: User suspended
  400:
    description: Invalid input
  403:
    description: Forbidden
    """
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
    """
Deactivate user (admin only)
---
tags:
  - admin
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required: [user_id]
      properties:
        user_id:
          type: integer
        suspension_reason:
          type: string
responses:
  200:
    description: User deactivated
  400:
    description: Invalid input
  403:
    description: Forbidden
"""
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
    """
Update user account status (admin only)
---
tags:
  - admin
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - user_id
        - account_status
      properties:
        user_id:
          type: integer
        account_status:
          type: string
        suspension_reason:
          type: string
responses:
  200:
    description: User updated
  400:
    description: Invalid input
  403:
    description: Forbidden
    """
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
    """
Get active coaches (admin only)
---
tags:
  - admin
responses:
  200:
    description: List of active coaches
    schema:
      type: object
      properties:
        message:
          type: string
        coaches:
          type: array
          items:
            type: object
            properties:
              user_id:
                type: integer
              first_name:
                type: string
              last_name:
                type: string
              name:
                type: string
              email:
                type: string
              coach_description:
                type: string
              price:
                type: number
              contract_count:
                type: integer
              certifications:
                type: array
                items:
                  type: object
                  properties:
                    cert_name:
                      type: string
                    provider_name:
                      type: string
                    description:
                      type: string
                    issued_date:
                      type: string
                      format: date-time
                    expires_date:
                      type: string
                      format: date-time
  403:
    description: Forbidden
    """
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